"""Hình `data` của các route thị trường. Envelope bọc ngoài nằm ở `haido_core.domain.envelope`.

Mã vai trò, cấp bậc, thành phố, nhóm kỹ năng là chuỗi snake_case tạm, chỉ dữ liệu biết;
#16 chốt mã thật. Ở đây không có enum nào cho chúng.
"""

import math
from collections import Counter
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from haido_api.schemas.skills import SkillCode
from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CellId, Meta, Ordinal, Stat, sample_n

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True, revalidate_instances="always")


class CityShareRow(BaseModel):
    """Tỷ trọng của một thành phố trong số tin của vai trò, trên toàn quốc (FR-33)."""

    model_config = _CONFIG

    city: str
    """Mã thành phố. `other` gom các thành phố khác, `unknown` là tin không xác định thành phố."""

    share: Stat
    """Tỷ trọng, `kind = composition_share`. Dưới ngưỡng mẫu vẫn có giá trị, kèm `low_sample_shown`."""

    @model_validator(mode="after")
    def _loai_thuoc_do(self) -> Self:
        if self.share.kind is not MeasureKind.COMPOSITION_SHARE:
            raise ValueError(f"share phải là composition_share, nhận {self.share.kind}.")
        return self


class CitySharesData(BaseModel):
    """`data` của `GET /api/v1/city-shares`."""

    model_config = _CONFIG

    role: str
    """Vai trò đã chọn; `all` là mọi vai trò."""

    level: str
    """Cấp bậc lọc đã dùng (#163): `all` là mọi cấp bậc, `entry` là nhóm mới vào nghề, hoặc một cấp như `senior`."""

    years: str = "any"
    """Mốc số năm kinh nghiệm đã dùng (#280): `any` là mọi số năm (gồm tin không ghi), `N` là tin yêu cầu tối thiểu
    không quá N năm."""

    years_unstated_cell_id: CellId | None = None
    """Ô toàn quốc của các tin (cụm) của vai trò ở cấp đã chọn không ghi số năm, nên không được tính ở mốc `N`
    (#280). Số tin là `meta.cells[years_unstated_cell_id].n`. `null` khi `years = any`."""

    total_cell_id: CellId
    """Ô toàn quốc của vai trò ở cấp và mốc số năm đã chọn, mẫu số của mọi tỷ trọng. Cỡ mẫu ở
    `meta.cells[total_cell_id]`."""

    rows: Annotated[list[CityShareRow], Field(min_length=1)]
    """Mỗi thành phố một dòng, cộng dòng `other` và `unknown`. Tổng `share.value` bằng 1."""

    @model_validator(mode="after")
    def _tong_bang_mot(self) -> Self:
        if (self.years == "any") != (self.years_unstated_cell_id is None):
            raise ValueError("years_unstated_cell_id phải là null khi years = any và có giá trị khi years là một mốc.")
        trung = sorted(city for city, k in Counter(r.city for r in self.rows).items() if k > 1)
        if trung:
            raise ValueError(f"Mã thành phố bị trùng: {', '.join(trung)}.")
        thieu = [row.city for row in self.rows if row.share.value is None]
        if thieu:
            raise ValueError(f"Tỷ trọng phải có giá trị, thiếu ở: {', '.join(thieu)}.")
        total = math.fsum(row.share.value for row in self.rows if row.share.value is not None)
        if not math.isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(f"Tổng tỷ trọng phải bằng 1, nhận {total}.")
        return self


class SkillRateRow(BaseModel):
    """Tỷ lệ xuất hiện của một kỹ năng trong ô đã dùng."""

    model_config = _CONFIG

    skill: str
    """Mã kỹ năng, snake_case (#205), ví dụ `spring_boot`."""

    rate: Stat
    """Tỷ lệ xuất hiện, `kind = skill_rate`. Dưới ngưỡng mẫu là `null_data`, không có giá trị."""

    group: str | None
    """Nhóm kỹ năng theo θ: `core`, `common`, `company_specific`. `null` khi `rate` bị ẩn (`null_data`)."""

    have: bool = False
    """Mã kỹ năng có trong `have=` của request (AD-22, #149). Web tick theo cờ này, không tự so mã."""

    @model_validator(mode="after")
    def _nhom_theo_hien_thi(self) -> Self:
        if self.rate.kind is not MeasureKind.SKILL_RATE:
            raise ValueError(f"rate phải là skill_rate, nhận {self.rate.kind}.")
        if self.rate.display is DisplayState.NULL_DATA and self.group is not None:
            raise ValueError("rate là null_data thì group phải là null.")
        if self.rate.display is not DisplayState.NULL_DATA and self.group is None:
            raise ValueError("rate có giá trị thì group phải có.")
        return self


class SkillRatesData(BaseModel):
    """`data` của `GET /api/v1/skill-rates`."""

    model_config = _CONFIG

    role: str
    """Vai trò người dùng chọn."""

    level: str
    """Cấp bậc người dùng chọn."""

    cell_id: CellId
    """Ô thật sự dùng để tính. Khác ô đã chọn khi quay về ô rộng hơn; lý do ở `fallback_label`."""

    rows: list[SkillRateRow]
    """Mỗi kỹ năng của ô một dòng, theo thứ tự hiển thị: dòng có tỷ lệ trước, tỷ lệ giảm dần, rồi mã kỹ năng (#149).
    Web không sắp xếp lại."""

    core_size: Ordinal | None = None
    """Số dòng `group = core`. `null` khi mọi `rate` là `null_data` (chưa đủ dữ liệu để chia nhóm)."""

    have_core: Ordinal | None = None
    """Số dòng core có `have` (AD-22: web không đếm). `null` cùng lúc với `core_size`."""

    @model_validator(mode="after")
    def _cung_mot_o(self) -> Self:
        lech = sorted({row.rate.cell_id for row in self.rows} - {self.cell_id})
        if lech:
            raise ValueError(f"Mọi rate phải thuộc ô {self.cell_id!r}, có ô lạ: {', '.join(lech)}.")
        if (self.core_size is None) != (self.have_core is None):
            raise ValueError("core_size và have_core cùng null hoặc cùng có giá trị.")
        if self.core_size is not None and self.have_core is not None:
            core = [row for row in self.rows if row.group == "core"]
            if self.core_size != len(core) or self.have_core != sum(row.have for row in core):
                raise ValueError("core_size/have_core phải khớp các dòng core và cờ have của chúng.")
        return self


class NewcomerRoleRow(BaseModel):
    """Một vai trò trên màn người mới (#110): số tin entry-level, tỷ lệ, và n.

    Hai con số đếm nằm ở `meta.cells`: số tin entry-level là `meta.cells[entry_cell_id].n`,
    n của vai trò là `meta.cells[total_cell_id].n`.
    """

    model_config = _CONFIG

    role: str
    """Mã vai trò."""

    total_cell_id: CellId
    """Ô toàn quốc của vai trò (`vn.<role>`); `n` của ô là số tin của vai trò, mẫu số của `share`."""

    entry_cell_id: CellId
    """Ô entry-level của vai trò (`vn.<role>.entry`); `n` của ô là số tin entry-level."""

    share: Stat
    """Tỷ lệ tin entry-level trong số tin của vai trò, `kind = level_share`, `cell_id = total_cell_id`.
    Vai trò dưới ngưỡng mẫu là `null_data`, không có giá trị."""

    @model_validator(mode="after")
    def _ty_le_cua_vai_tro(self) -> Self:
        if self.share.kind is not MeasureKind.LEVEL_SHARE:
            raise ValueError(f"share phải là level_share, nhận {self.share.kind}.")
        if self.share.cell_id != self.total_cell_id:
            raise ValueError(
                f"share.cell_id phải là total_cell_id {self.total_cell_id!r}, nhận {self.share.cell_id!r}."
            )
        if self.entry_cell_id == self.total_cell_id:
            raise ValueError("entry_cell_id phải khác total_cell_id.")
        return self


class NewcomerRolesData(BaseModel):
    """`data` của `GET /api/v1/newcomer-roles`."""

    model_config = _CONFIG

    levels: Annotated[list[str], Field(min_length=1)]
    """Các cấp bậc được tính là entry-level, ví dụ `["intern", "fresher", "junior"]`."""

    rows: Annotated[list[NewcomerRoleRow], Field(min_length=1)]
    """Mỗi vai trò một dòng, theo thứ tự hiển thị: dòng có tỷ lệ trước, rồi dòng `null_data`;
    trong mỗi nhóm, số tin entry-level giảm dần rồi theo mã vai trò. Web không sắp xếp lại."""

    @model_validator(mode="after")
    def _khong_trung_vai_tro(self) -> Self:
        trung = sorted(role for role, k in Counter(r.role for r in self.rows).items() if k > 1)
        if trung:
            raise ValueError(f"Mã vai trò bị trùng: {', '.join(trung)}.")
        return self


SKILL_ROLES_LEVEL_GROUP = "entry"
"""Nhóm cấp bậc cố định của `skill-roles` (DEC-8, #134): Intern, Fresher, Junior gộp một."""


class SkillLabel(BaseModel):
    """Kỹ năng đã dùng, để màn ghi rõ nó khớp kỹ năng nào (AC 1 của #113)."""

    model_config = _CONFIG

    code: SkillCode
    """Mã kỹ năng trong bộ từ vựng, snake_case."""

    name_en: Annotated[str, Field(min_length=1)]
    """Tên tiếng Anh. Tên công nghệ, nên được có chữ số (`Python3`, `ISO 27001`) ngoài quy tắc DEC-6."""

    name_vi: Annotated[str, Field(min_length=1)]
    """Tên tiếng Việt, cùng quy tắc."""


class SkillRoleRow(BaseModel):
    """Tỷ lệ tin entry-level của một vai trò có nhắc kỹ năng (#166). Cỡ mẫu của tỷ lệ là
    `meta.cells[share.cell_id].n_by_measure["skill_count"]` (số tin đã quét kỹ năng, `n_scanned` của #101); `meta.cells[..].n`
    vẫn là số tin của ô, cùng số với `newcomer-roles`."""

    model_config = _CONFIG

    role: str
    """Mã vai trò."""

    share: Stat
    """Tỷ lệ, `kind = skill_rate`, `cell_id = vn.<role>.entry`. Dưới ngưỡng mẫu (theo `skill_count`, không theo `n` của
    ô) là `null_data`, không có giá trị; cỡ mẫu đó vẫn có ở `meta.cells` để màn ghi "not enough data (n/min_sample)".
    Đủ mẫu mà không tin nào nhắc là 0, không phải null."""

    @model_validator(mode="after")
    def _ty_le_cua_o_entry(self) -> Self:
        if self.share.kind is not MeasureKind.SKILL_RATE:
            raise ValueError(f"share phải là skill_rate, nhận {self.share.kind}.")
        expected = f"vn.{self.role}.{SKILL_ROLES_LEVEL_GROUP}"
        if self.share.cell_id != expected:
            raise ValueError(f"share.cell_id phải là {expected!r}, nhận {self.share.cell_id!r}.")
        return self


class SkillRolesData(BaseModel):
    """`data` của `GET /api/v1/skill-roles`."""

    model_config = _CONFIG

    skill: SkillLabel
    """Kỹ năng đã chọn, kèm tên."""

    level: str
    """Mã nhóm cấp bậc của mọi dòng (`entry`), cùng mã với tham số `level` của `skill-rates` và của `/ho-so-ky-nang`, để
    màn mở hồ sơ kỹ năng của một vai trò đúng cấp (#169, #111)."""

    levels: Annotated[list[str], Field(min_length=1)]
    """Các cấp bậc được tính là entry-level, ví dụ `["intern", "fresher", "junior"]`."""

    mentioned: bool
    """`false` khi không tin tuyển dụng hiện tại nào, ở cấp bậc nào, nhắc kỹ năng (AC 4 của #113): không chỉ entry-level,
    và kể cả khi mọi ô entry-level bị ẩn. Máy chủ tính từ ô mọi cấp; web không suy từ các dòng (AD-22). `true` mà mọi
    dòng hiện đều 0 là hợp lệ: tin nhắc nằm ở cấp khác hoặc ở ô dưới ngưỡng bị ẩn."""

    rows: Annotated[list[SkillRoleRow], Field(min_length=1)]
    """Mỗi vai trò một dòng, theo thứ tự hiển thị: dòng có tỷ lệ trước, tỷ lệ giảm dần rồi theo mã vai trò; sau đó dòng
    `null_data`, cỡ mẫu của phép đo giảm dần rồi theo mã vai trò. Web không sắp xếp lại."""

    @model_validator(mode="after")
    def _dong_nhat_quan(self) -> Self:
        if self.level != SKILL_ROLES_LEVEL_GROUP:
            raise ValueError(f"level phải là {SKILL_ROLES_LEVEL_GROUP!r}, nhận {self.level!r}.")
        trung = sorted(role for role, k in Counter(r.role for r in self.rows).items() if k > 1)
        if trung:
            raise ValueError(f"Mã vai trò bị trùng: {', '.join(trung)}.")
        shown = [r for r in self.rows if r.share.value is not None]
        hidden_from = next((i for i, r in enumerate(self.rows) if r.share.value is None), len(self.rows))
        if len(shown) != hidden_from:
            raise ValueError("Sai thứ tự: dòng null_data phải đứng sau mọi dòng có tỷ lệ.")
        keys = [(-(r.share.value or 0.0), r.role) for r in shown]
        if keys != sorted(keys):
            raise ValueError("Sai thứ tự: dòng có tỷ lệ phải theo tỷ lệ giảm dần rồi theo mã vai trò.")
        if not self.mentioned and any(r.share.value for r in shown):
            raise ValueError("mentioned = false nhưng có dòng hiện tỷ lệ lớn hơn 0.")
        return self

    def check_against_meta(self, meta: Meta) -> list[str]:
        """Thứ tự dòng `null_data` cần cỡ mẫu nên chỉ kiểm được cùng `meta` (gọi bởi `Envelope`): cỡ mẫu của phép đo giảm
        dần rồi mã vai trò, cả với nguồn thật (#168)."""
        hidden = [r for r in self.rows if r.share.value is None]
        sizes: dict[str, int] = {}
        for row in hidden:
            cell = meta.cells.get(row.share.cell_id)
            if cell is None:
                return []  # thiếu ô là lỗi của Envelope, không báo thêm ở đây
            sizes[row.role] = sample_n(row.share.kind, cell.n, cell.n_by_measure)
        keys = [(-sizes[r.role], r.role) for r in hidden]
        if keys != sorted(keys):
            return ["data.rows: dòng null_data phải theo cỡ mẫu của phép đo giảm dần rồi theo mã vai trò"]
        return []


class OverviewShare(BaseModel):
    """Một tỷ trọng có mã trên màn toàn cảnh (#327): một cấp bậc, một nơi làm việc, hay một mốc số năm."""

    model_config = _CONFIG

    code: str
    """Mã cấp bậc (`intern`…`lead`, `unknown`), mã nơi (`ha_noi`, `other_provinces`, `remote`…) hay mốc số năm
    (`0`, `1`, `4-5`, `over_5`, `none`)."""

    share: Stat
    """Tỷ trọng đã tính và đã qua `suppression_for` ở máy chủ. `n` của ô là số tin đếm được của phần này
    (tỷ trọng cấu phần) hoặc của cả nhóm (tỷ lệ cấp bậc)."""


class OverviewRole(BaseModel):
    """Một vai trò trên màn toàn cảnh (#327)."""

    model_config = _CONFIG

    role: str
    """Mã vai trò."""

    cell_id: CellId
    """Ô toàn quốc của vai trò (`vn.<role>`); `n` là số tin của vai trò, `seniority_mix` là số tin theo cấp."""

    entry_cell_id: CellId
    """Ô entry-level của vai trò (`vn.<role>.entry`); `n` là số tin Intern, Fresher, Junior."""

    share: Stat
    """Tỷ trọng của vai trò trong mọi tin IT, `composition_share`, `cell_id = cell_id`."""

    entry_share: Stat
    """Tỷ lệ tin entry-level trong số tin của vai trò, `level_share`, `cell_id = cell_id`."""

    level_mix: list[OverviewShare]
    """Tỷ lệ từng cấp trong số tin của vai trò, `level_share`, theo thứ tự `MarketOverviewData.levels`."""

    places: list[OverviewShare]
    """Tỷ trọng Hà Nội và TP.HCM trong số tin của vai trò, `composition_share`, ô `<city>.<role>`."""


class OverviewRanking(BaseModel):
    """Thứ tự vai trò theo số tin ở một cấp (#329): biểu đồ vai trò cạnh biểu đồ tròn đổi theo cấp đã chọn."""

    model_config = _CONFIG

    level: str
    """Mã cấp."""

    roles: list[str]
    """Mọi vai trò: nhiều tin ở cấp này trước, cùng số tin thì theo mã; `other` luôn ở cuối."""


class MarketOverviewData(BaseModel):
    """`data` của `GET /api/v1/market-overview` (#327): toàn cảnh thị trường của một snapshot, mọi tỷ trọng đã tính."""

    model_config = _CONFIG

    total_cell_id: CellId
    """Ô toàn quốc mọi vai trò (`vn.all`); `n` là số tin IT đang mở, `seniority_mix` là số tin theo cấp."""

    entry_cell_id: CellId
    """Ô entry-level toàn quốc (`vn.all.entry`)."""

    levels: Annotated[list[str], Field(min_length=1)]
    """Cấp bậc theo thứ tự hiển thị: từng cấp chi tiết của `config/rules.toml`, `unknown` ở cuối."""

    entry_levels: Annotated[list[str], Field(min_length=1)]
    """Các cấp tính là mới vào nghề, ví dụ `["intern", "fresher", "junior"]`."""

    level_mix: list[OverviewShare]
    """Tỷ lệ từng cấp trong mọi tin IT, `level_share`, ô `total_cell_id`, theo thứ tự `levels`."""

    entry_share: Stat
    """Tỷ lệ tin entry-level trong mọi tin IT, `level_share`, ô `total_cell_id`."""

    big_cities_share: Stat
    """Tỷ trọng tin ở Hà Nội hoặc TP.HCM, `composition_share`, ô `big_cities.all`."""

    roles: Annotated[list[OverviewRole], Field(min_length=1)]
    """Mỗi vai trò một dòng: nhiều tin trước, cùng số tin thì theo mã; `other` luôn ở cuối. Web không sắp xếp lại."""

    places: Annotated[list[OverviewShare], Field(min_length=1)]
    """Nơi làm việc theo thứ tự hiển thị: Hà Nội, TP.HCM, Đà Nẵng, các tỉnh khác gộp (`other_provinces`), làm từ xa,
    nước ngoài, không xác định. `composition_share`, ô `<city>.all`."""

    levels_by_size: list[str]
    """Các cấp (trừ `unknown`), nhiều tin trước, cùng số tin thì theo thứ tự `levels`. Câu tóm tắt đọc từ đây."""

    roles_by_level: list[OverviewRanking]
    """Mỗi cấp của `levels` một thứ tự vai trò, theo đúng thứ tự `levels`."""

    roles_by_entry_share: list[str]
    """Vai trò có tỷ lệ người mới hiện được (trừ `other`), tỷ lệ cao trước, cùng tỷ lệ thì theo mã."""

    years: Annotated[list[OverviewShare], Field(min_length=1)]
    """Số năm kinh nghiệm tối thiểu tin yêu cầu, theo mốc của `config/rules.toml`: `0`, `1`, …, `over_<mốc cuối>`,
    rồi `none` (tin không ghi). `composition_share`, ô `vn.all.years_<mã>`; các phần cộng lại bằng `n` toàn quốc."""

    @model_validator(mode="after")
    def _nhat_quan(self) -> Self:
        if [s.code for s in self.level_mix] != self.levels:
            raise ValueError("level_mix phải theo đúng thứ tự levels.")
        if not set(self.entry_levels) <= set(self.levels):
            raise ValueError("entry_levels phải nằm trong levels.")
        kinds = (
            [(f"level_mix[{s.code}]", s.share, MeasureKind.LEVEL_SHARE) for s in self.level_mix]
            + [("entry_share", self.entry_share, MeasureKind.LEVEL_SHARE)]
            + [("big_cities_share", self.big_cities_share, MeasureKind.COMPOSITION_SHARE)]
            + [(f"places[{s.code}]", s.share, MeasureKind.COMPOSITION_SHARE) for s in self.places]
            + [(f"years[{s.code}]", s.share, MeasureKind.COMPOSITION_SHARE) for s in self.years]
        )
        for row in self.roles:
            kinds += [(f"roles[{row.role}].share", row.share, MeasureKind.COMPOSITION_SHARE)]
            kinds += [(f"roles[{row.role}].entry_share", row.entry_share, MeasureKind.LEVEL_SHARE)]
            kinds += [(f"roles[{row.role}].level_mix", s.share, MeasureKind.LEVEL_SHARE) for s in row.level_mix]
            kinds += [(f"roles[{row.role}].places", s.share, MeasureKind.COMPOSITION_SHARE) for s in row.places]
            if [s.code for s in row.level_mix] != self.levels:
                raise ValueError(f"roles[{row.role}].level_mix phải theo đúng thứ tự levels.")
        sai = [path for path, stat, kind in kinds if stat.kind is not kind]
        if sai:
            raise ValueError(f"Sai loại thước đo ở: {', '.join(sai)}.")
        trung = sorted(role for role, k in Counter(r.role for r in self.roles).items() if k > 1)
        if trung:
            raise ValueError(f"Mã vai trò bị trùng: {', '.join(trung)}.")
        role_set = {r.role for r in self.roles}
        if [r.level for r in self.roles_by_level] != self.levels:
            raise ValueError("roles_by_level phải theo đúng thứ tự levels.")
        if any(sorted(r.roles) != sorted(role_set) for r in self.roles_by_level):
            raise ValueError("Mỗi thứ tự trong roles_by_level phải gồm đúng các vai trò của roles.")
        if sorted(self.levels_by_size) != sorted(lv for lv in self.levels if lv != "unknown"):
            raise ValueError("levels_by_size phải gồm đúng các cấp của levels trừ unknown.")
        if not set(self.roles_by_entry_share) <= role_set:
            raise ValueError("roles_by_entry_share có vai trò lạ.")
        return self
