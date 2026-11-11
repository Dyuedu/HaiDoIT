"""Bước `aggregate`: tỷ trọng thành phố của snapshot S, ghi `stat_cells`, `stat_city_shares` và `stat_sources` (#93).

Thứ tự các bước là `ingest → lifecycle → aggregate → publish`. Bước này đọc dữ kiện tại S
(`facts_at`) và dòng vòng đời tại S, phân loại từng tin bằng `RuleClassifier`, đổi nhãn tiếng
Việt sang mã snake_case theo bảng ở `config/rules.toml`, rồi giao cho `aggregate_city_shares`
đếm. Hai tin cùng công ty và chức danh đã chuẩn hóa là một cụm (#100): nhãn lấy từ tin đại diện,
`last_seen` là ngày thấy gần nhất của các thành viên. Nhãn chưa có trong bảng thì dừng, không đoán mã.

Tin của nguồn trong `sources.excluded` (linkedin, #263) bị bỏ ngay từ đầu: không phân loại, không vào ô nào,
không làm nguồn nào được liệt kê. `stat_job_lifecycle` vẫn có dòng của các tin này (không phải số công khai,
API không đọc).

Mỗi vai trò có thêm ô và tỷ trọng thành phố cho từng cấp bậc lọc được của bản đồ (#163): `all`, nhóm `entry` và từng
cấp, theo `level_options` và `level_groups` trong `config/rules.toml`. Cột `seniority` của hai bảng là mã cấp lọc.

`stat_sources` là các nguồn có ít nhất một tin được đếm trong cửa sổ của S (#259, DEC-12), không phải
các nguồn có lượt chạy ở S. API đọc danh sách này theo khóa.

Tin không có dòng vòng đời tại S (chỉ thấy ở lượt chạy lỗi, AD-4) không được đếm. Nếu `ingest`
chạy lại cho S thì phải chạy lại `lifecycle` trước khi `aggregate`.

Mọi hàng của S ghi trong một transaction. Chạy lại cho S đang `open` ra cùng hàng; S đã
`published` hoặc `partial` thì từ chối và không ghi gì.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import Engine

from haido_core.config import RulesConfig
from haido_core.db import snapshot_store
from haido_core.domain.aggregate import aggregate_city_shares, sources_in_window
from haido_core.domain.classify import (
    RuleClassifier,
    counts_in_aggregate,
    default_classify_config,
)
from haido_core.domain.cluster import ClusterMember, collapse_clusters
from haido_core.domain.population import CountedPosting
from haido_core.domain.registry import PostingFacts
from haido_core.steps.common import SnapshotClosedError, StepError, parse_snapshot_id


@dataclass(frozen=True, slots=True)
class AggregateResult:
    snapshot_id: date
    cells: int
    shares: int
    sources: tuple[str, ...]
    config_version: str


def _code(table: dict[str, str], kind: str, name: str, label: str) -> str:
    code = table.get(label)
    if code is None:
        raise StepError(
            f"Nhãn {kind} {label!r} chưa có trong bảng labels.{name} của config/rules.toml; "
            "thêm vào bảng rồi chạy lại, bước này không đoán mã."
        )
    return code


def aggregate_snapshot(snapshot_id: str, *, engine: Engine, rules: RulesConfig) -> AggregateResult:
    day = parse_snapshot_id(snapshot_id)
    classifier = RuleClassifier(default_classify_config())
    with engine.begin() as conn:
        status = snapshot_store.lock_status(conn, day)
        if status is None:
            raise StepError(f"Snapshot {day.isoformat()} chưa mở; chạy `haido ingest` trước.")
        if status != "open":
            raise SnapshotClosedError(
                f"Snapshot {day.isoformat()} đã chốt (trạng thái {status}); không ghi thêm. "
                "Tính lại phải sinh snapshot mới."
            )
        missing = snapshot_store.unaccounted_postings(conn, day)
        if missing:
            raise StepError(
                f"Snapshot {day.isoformat()} có {missing} tin thấy ở lượt chạy thành công nhưng chưa có dòng "
                "vòng đời mới; chạy lại `haido lifecycle` trước."
            )
        excluded = set(rules.excluded_sources)
        lives = [row for row in snapshot_store.lifecycle_postings(conn, day) if row[1].strip().lower() not in excluded]
        facts = snapshot_store.facts_at(conn, day)
        urls = snapshot_store.posting_urls(conn, [posting_id for posting_id, _, _ in lives])
        empty = snapshot_store.FactVersion(None, None, None, None, None)
        members: list[ClusterMember] = []
        last_seen: dict[str, date] = {}
        for posting_id, source, seen in lives:
            fact = facts.get(posting_id, empty)
            member_id = str(posting_id)
            members.append(
                ClusterMember(
                    member_id,
                    source,
                    urls.get(posting_id, ""),
                    fact.company,
                    fact.title,
                    fact.location_text,
                    fact.experience_level,
                    fact.job_level,
                )
            )
            last_seen[member_id] = seen
        by_id = {member.posting_id: member for member in members}
        clusters = collapse_clusters(members, source_rank=rules.source_priority)
        rep_inputs = []
        for cluster in clusters:
            rep = by_id[cluster.representative_id]
            fact = facts.get(int(rep.posting_id), empty)
            level_text = " ".join(part for part in (fact.job_level, fact.experience_level) if part)
            rep_inputs.append(PostingFacts(fact.title or "", rep.source, None, level_text or None, fact.location_text))
        results = classifier.classify(rep_inputs)
        assert isinstance(results, tuple)
        counted = []
        source_rows: list[tuple[str, date]] = []
        for cluster, result in zip(clusters, results, strict=True):
            if not counts_in_aggregate(result):
                continue
            counted.append(
                CountedPosting(
                    cluster_id=cluster.cluster_id,
                    last_seen=max(last_seen[member_id] for member_id in cluster.member_ids),
                    role=_code(rules.role_codes, "vai trò", "role", result.role),
                    city=_code(rules.city_codes, "thành phố", "city", result.city),
                    seniority=_code(rules.level_codes, "cấp bậc", "level", result.seniority),
                )
            )
            for member_id in cluster.member_ids:
                source_rows.append((by_id[member_id].source, last_seen[member_id]))
        try:
            aggregate = aggregate_city_shares(
                day,
                counted,
                roles=rules.roles,
                cities=tuple(rules.city_codes.values()),
                levels=tuple(rules.level_codes.values()),
                window_days=rules.window_days,
                level_options=rules.level_options,
                level_groups=rules.level_groups,
            )
        except ValueError as exc:
            raise StepError(f"Không tổng hợp được snapshot {day.isoformat()}: {exc}") from exc
        sources = sources_in_window(day, source_rows, window_days=rules.window_days)
        snapshot_store.replace_stats(conn, day, rules.config_version, aggregate.cells, aggregate.shares, sources)
    return AggregateResult(day, len(aggregate.cells), len(aggregate.shares), sources, rules.config_version)
