"""Phép 7, phần gộp cụm (#100).

Khóa cụm là công ty và chức danh đã chuẩn hóa. Thiếu một trong hai thì tin đứng riêng.
Đại diện chọn theo hạng nguồn, rồi số trường thống kê, rồi URL. Hàm thuần, không xóa tin.
"""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass

_DROP = frozenset({"tnhh", "ctcp", "jsc", "inc", "llc", "ltd", "limited", "corp", "corporation", "co", "cp"})


def _company_tokens(value: str | None) -> list[str]:
    """Bỏ tiền tố 'công ty' và token pháp lý. Giữ lại tên nếu bỏ hết thì rỗng."""
    tokens = _tokens(value)
    if len(tokens) >= 2 and tuple(tokens[:2]) == ("cong", "ty"):
        tokens = tokens[2:]
    elif tokens and tokens[0] in {"cty", "company"}:
        tokens = tokens[1:]
    changed = True
    while changed:
        changed = False
        for index in range(len(tokens) - 1):
            if (tokens[index], tokens[index + 1]) == ("co", "phan"):
                del tokens[index : index + 2]
                changed = True
                break
    kept = [token for token in tokens if token not in _DROP]
    return kept or tokens


def _fold(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "d")
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold()


def _tokens(value: str | None) -> list[str]:
    cleaned = re.sub(r"[^\w\s]", " ", _fold(value or ""), flags=re.UNICODE)
    return [token for token in cleaned.split() if token]


def identity_key(company: str | None, title: str | None) -> str | None:
    """Khóa danh tính. `None` khi công ty hoặc chức danh không còn token."""
    firm = _company_tokens(company)
    role = _tokens(title)
    if not firm or not role:
        return None
    return f"{' '.join(firm)}\t{' '.join(role)}"


@dataclass(frozen=True, slots=True)
class ClusterMember:
    """Một tin đem đi gộp. Năm trường thống kê là chức danh, công ty, địa điểm, kinh nghiệm, cấp bậc."""

    posting_id: str
    source: str
    url: str
    company: str | None
    title: str | None
    location_text: str | None
    experience_level: str | None
    job_level: str | None


@dataclass(frozen=True, slots=True)
class Cluster:
    cluster_id: str
    representative_id: str
    member_ids: tuple[str, ...]


def _filled(member: ClusterMember) -> int:
    fields = (member.title, member.company, member.location_text, member.experience_level, member.job_level)
    return sum(1 for value in fields if value is not None and value.strip())


def _ranks(source_rank: Sequence[str]) -> dict[str, int]:
    return {name.casefold().strip(): index for index, name in enumerate(source_rank)}


def choose_representative(members: Sequence[ClusterMember], *, source_rank: Sequence[str]) -> ClusterMember:
    """Phần tử đầu theo hạng nguồn, số trường, URL có giá trị rồi A–Z, rồi mã tin."""
    if not members:
        raise ValueError("Cụm không có tin.")
    ranks = _ranks(source_rank)
    last = len(ranks)

    def key(member: ClusterMember) -> tuple[object, ...]:
        url = member.url.strip()
        return (
            ranks.get(member.source.casefold().strip(), last),
            -_filled(member),
            url == "",
            url,
            member.posting_id,
        )

    return min(members, key=key)


def collapse_clusters(members: Sequence[ClusterMember], *, source_rank: Sequence[str]) -> tuple[Cluster, ...]:
    """Gộp tin cùng khóa. Cùng đầu vào thì cùng cụm và cùng đại diện, không phụ thuộc thứ tự."""
    seen: set[str] = set()
    for member in members:
        if member.posting_id in seen:
            raise ValueError(f"Mã tin {member.posting_id} lặp.")
        seen.add(member.posting_id)
    groups: dict[str, list[ClusterMember]] = {}
    for member in members:
        key = identity_key(member.company, member.title)
        group_id = f"k:{key}" if key is not None else f"p:{member.posting_id}"
        groups.setdefault(group_id, []).append(member)
    clusters: list[Cluster] = []
    for cluster_id in sorted(groups):
        group = groups[cluster_id]
        representative = choose_representative(group, source_rank=source_rank)
        clusters.append(
            Cluster(
                cluster_id=cluster_id,
                representative_id=representative.posting_id,
                member_ids=tuple(sorted(member.posting_id for member in group)),
            )
        )
    return tuple(clusters)
