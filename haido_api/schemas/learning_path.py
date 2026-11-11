"""Hình `data` của `GET /api/v1/learning-path` (#212). Envelope bọc ngoài nằm ở `haido_core.domain.envelope`.

Lộ trình đã xếp sẵn (AD-7). **Chặng là thuộc tính của từng nút kỹ năng**, không phụ thuộc `have`: lọc theo
`have` không đổi chặng hay thứ tự, chỉ đổi cờ `have` và các số đếm (AD-22). Khóa xếp trong một chặng theo FR-22:
(nhóm, tỷ lệ giảm dần, mã kỹ năng A–Z).
"""

import re
from collections import Counter
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CellId, Ordinal, Stat
from haido_core.vocab.skills import is_skill_code

_CONFIG = ConfigDict(
    extra="forbid", use_attribute_docstrings=True, revalidate_instances="always"
)
_GROUP_RANK: dict[str | None, int] = {
    "core": 0,
    "common": 1,
    "company_specific": 2,
    None: 3,
}
_HTTPS = re.compile(r"https://\S+")

SkillCode = Annotated[str, Field(max_length=40)]


class PathStatus(StrEnum):
    READY = "ready"
    """Vai trò có lộ trình đã rà soát."""

    NOT_READY = "not_ready"
    """Chưa có lộ trình đã rà soát: không có chặng; web gợi ý hồ sơ kỹ năng (`skill-rates`)."""


class PathResource(BaseModel):
    """Một tài liệu miễn phí cho kỹ năng."""

    model_config = _CONFIG

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    """Tên tài liệu."""

    url: str
    """Link `https://`."""

    @model_validator(mode="after")
    def _link_https(self) -> Self:
        if not _HTTPS.fullmatch(self.url):
            raise ValueError("url phải là link https.")
        return self


class PathSkill(BaseModel):
    """Một kỹ năng trên lộ trình."""

    model_config = _CONFIG

    skill: SkillCode
    """Mã kỹ năng, snake_case (#205), có trong bộ từ vựng."""

    rate: Stat
    """Tỷ lệ xuất hiện, `kind = skill_rate`, `cell_id = data.cell_id`. Khớp `skill-rates` cùng ô."""

    group: str | None
    """`core`, `common`, `company_specific`; `null` khi `rate` là `null_data` (như `SkillRateRow`)."""

    foundation_for: list[SkillCode]
    """Không rỗng khi đây là kỹ năng nền tảng (FR-20): mã các kỹ năng `core` hoặc `common` trên lộ trình mà nó là tổ
    tiên, bắc cầu qua `prerequisite_for` (cháu cũng tính), xếp A–Z. Mỗi mã đều đi tới được từ kỹ năng này qua
    `prerequisite_for`. Rỗng khi `group` bị ẩn (`null`): chưa biết nhóm của ai nên không ghi nền tảng.
    Web ghi "Kỹ năng nền tảng (cần cho X)"."""

    prerequisite_for: list[SkillCode]
    """Mã các kỹ năng trên lộ trình cần kỹ năng này trực tiếp (chỉ cạnh trực tiếp, không bắc cầu); luôn ở chặng sau."""

    have: bool
    """Đã có trong `?have=`."""

    blurb: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    """Lời dẫn viết sẵn: không chữ số ngoài tên công nghệ, không `%` (FR-23)."""

    resource: PathResource
    """Một tài liệu miễn phí."""

    @model_validator(mode="after")
    def _kiem_tung_ky_nang(self) -> Self:
        if not is_skill_code(self.skill):
            raise ValueError(f"Mã kỹ năng sai định dạng: {self.skill!r}.")
        if self.rate.kind is not MeasureKind.SKILL_RATE:
            raise ValueError(f"rate phải là skill_rate, nhận {self.rate.kind}.")
        hidden = self.rate.display is DisplayState.NULL_DATA
        if hidden and self.group is not None:
            raise ValueError("rate là null_data thì group phải là null.")
        if not hidden and self.group is None:
            raise ValueError("rate có giá trị thì group phải có.")
        if self.group == "company_specific" and not self.foundation_for:
            raise ValueError(
                f"{self.skill}: kỹ năng riêng công ty chỉ vào lộ trình khi là nền tảng (FR-20)."
            )
        return self


class PathStage(BaseModel):
    """Một chặng: các kỹ năng đã xếp thứ tự."""

    model_config = _CONFIG

    stage: Ordinal
    """Số chặng, từ 1, liền nhau."""

    skills: Annotated[list[PathSkill], Field(min_length=1)]
    """Theo khóa FR-22: nhóm (cốt lõi trước), tỷ lệ giảm dần, mã A–Z."""


def _reachable(direct: dict[str, list[str]], start: str) -> set[str]:
    """Mọi mã đi tới được từ `start` qua các cạnh trực tiếp (bắc cầu). Đồ thị đã được kiểm là tăng chặng."""
    seen: set[str] = set()
    todo = list(direct.get(start, ()))
    while todo:
        code = todo.pop()
        if code not in seen:
            seen.add(code)
            todo.extend(direct.get(code, ()))
    return seen


def order_key(skill: PathSkill) -> tuple[int, float, str]:
    return (_GROUP_RANK[skill.group], -(skill.rate.value or 0.0), skill.skill)


class LearningPathData(BaseModel):
    """`data` của `GET /api/v1/learning-path`."""

    model_config = _CONFIG

    role: str
    """Vai trò đã chọn."""

    level: str
    """Cấp bậc đã chọn."""

    status: PathStatus
    """`ready` hoặc `not_ready`. `not_ready` là kết quả bình thường (200), không phải lỗi."""

    cell_id: CellId | None
    """Ô cho các tỷ lệ; khác `entry_cell_id` khi quay về ô rộng hơn (`meta.cells[cell_id].fallback_label`).
    `null` khi `not_ready`."""

    entry_cell_id: CellId
    """Ô entry-level của vai trò; `meta.cells[entry_cell_id].n` là số tin entry-level (#221), có cả khi quay về."""

    stages: list[PathStage]
    """Các chặng đã xếp. Rỗng khi `not_ready`."""

    current_stage: Ordinal | None
    """Chặng đầu tiên còn kỹ năng `have = false`; `null` khi đã có hết hoặc `not_ready`."""

    have_on_path: Ordinal
    """Số kỹ năng trên lộ trình mà người dùng đã có ("N" của "N of M skills on this path")."""

    path_size: Ordinal
    """Số kỹ năng trên lộ trình ("M")."""

    have_ignored: list[SkillCode]
    """Mã hợp lệ trong `?have=` không có trên lộ trình này, xếp A–Z."""

    @model_validator(mode="after")
    def _trang_thai(self) -> Self:
        if self.status is PathStatus.NOT_READY:
            if self.stages:
                raise ValueError("not_ready thì không có chặng.")
            if self.cell_id is not None:
                raise ValueError("not_ready thì cell_id phải là null.")
            if self.current_stage is not None or self.have_on_path or self.path_size:
                raise ValueError(
                    "not_ready thì current_stage là null, have_on_path và path_size là 0."
                )
        else:
            if not self.stages:
                raise ValueError("ready thì phải có chặng.")
            if self.cell_id is None:
                raise ValueError("ready thì cell_id phải có.")
        return self

    @model_validator(mode="after")
    def _chang_va_thu_tu(self) -> Self:
        numbers = [s.stage for s in self.stages]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError(f"Các stage phải đánh số liền từ 1, nhận {numbers}.")
        for st in self.stages:
            keys = [order_key(s) for s in st.skills]
            if keys != sorted(keys):
                raise ValueError(
                    f"Chặng {st.stage} sai thứ tự FR-22 (nhóm, tỷ lệ giảm dần, mã A–Z)."
                )
        for s in self._skills():
            if self.cell_id is not None and s.rate.cell_id != self.cell_id:
                raise ValueError(
                    f"rate của {s.skill} thuộc ô {s.rate.cell_id!r}, phải là cell_id {self.cell_id!r}."
                )
        return self

    @model_validator(mode="after")
    def _tham_chieu(self) -> Self:
        skills = self._skills()
        trung = sorted(
            code for code, k in Counter(s.skill for s in skills).items() if k > 1
        )
        if trung:
            raise ValueError(f"Mã kỹ năng lặp trên lộ trình: {', '.join(trung)}.")
        stage_of = {s.skill: st.stage for st in self.stages for s in st.skills}
        for st in self.stages:
            for s in st.skills:
                for field, codes in (
                    ("prerequisite_for", s.prerequisite_for),
                    ("foundation_for", s.foundation_for),
                ):
                    for code in codes:
                        if code not in stage_of:
                            raise ValueError(
                                f"{s.skill}.{field}: {code} không có trên lộ trình."
                            )
                        if stage_of[code] <= st.stage:
                            raise ValueError(
                                f"{s.skill} (chặng {st.stage}) phải ở chặng trước {code} (chặng {stage_of[code]})."
                            )
        direct = {s.skill: s.prerequisite_for for s in skills}
        group_of = {s.skill: s.group for s in skills}
        for s in skills:
            if not s.foundation_for:
                continue
            reach = _reachable(direct, s.skill)
            for code in s.foundation_for:
                if code not in reach:
                    raise ValueError(
                        f"{s.skill}: foundation_for {code} không đi tới được qua prerequisite_for."
                    )
                if group_of[code] not in ("core", "common"):
                    raise ValueError(
                        f"{s.skill}: foundation_for {code} phải thuộc nhóm core hoặc common."
                    )
        return self

    @model_validator(mode="after")
    def _dem(self) -> Self:
        skills = self._skills()
        have = sum(1 for s in skills if s.have)
        if self.path_size != len(skills):
            raise ValueError(f"path_size phải là {len(skills)}, nhận {self.path_size}.")
        if self.have_on_path != have:
            raise ValueError(f"have_on_path phải là {have}, nhận {self.have_on_path}.")
        want = next(
            (st.stage for st in self.stages if any(not s.have for s in st.skills)), None
        )
        if self.current_stage != want:
            raise ValueError(
                f"current_stage phải là {want}, nhận {self.current_stage}."
            )
        if self.have_ignored != sorted(set(self.have_ignored)):
            raise ValueError("have_ignored phải xếp A–Z và không trùng.")
        on_path = {s.skill for s in skills}
        bad = [c for c in self.have_ignored if c in on_path or not is_skill_code(c)]
        if bad:
            raise ValueError(
                f"have_ignored chỉ gồm mã đúng định dạng và không có trên lộ trình, sai ở: {', '.join(bad)}."
            )
        return self

    def _skills(self) -> list[PathSkill]:
        return [s for st in self.stages for s in st.skills]
