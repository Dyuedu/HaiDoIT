"""FR-9, AD-17, AD-22 — hình response của "một kỹ năng qua các vai trò" (#166) và dữ liệu giả của nó.

`GET /api/v1/skill-roles?skill=<mã>`: mỗi vai trò của `config/rules.toml` một dòng, tỷ lệ tin entry-level (Intern + Fresher +
Junior) của vai trò có nhắc kỹ năng. Cỡ mẫu n là `meta.cells[share.cell_id].n`. Web không tính, không sắp xếp, không tự
suy "không tin nào nhắc kỹ năng này" (AD-22): máy chủ quyết thứ tự và cờ `mentioned`.
"""

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from haido_api.fake_market import FIXTURE, FakeMarket
from haido_api.main import app, create_app
from haido_api.market_source import UnknownSkill
from haido_api.routes.market import SOURCE_ENV, load_sources
from haido_api.schemas.market import SkillRoleRow, SkillRolesData
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import Envelope, Stat
from haido_core.vocab.skills import load_seed_skills

PATH = "/api/v1/skill-roles"
ENTRY_LEVELS = ["intern", "fresher", "junior"]
RAW = json.loads(FIXTURE.read_text(encoding="utf-8"))
ROOT = Path(__file__).resolve().parents[2]
SKILL = {"code": "python", "name_en": "Python", "name_vi": "Python"}


def _get(skill: str) -> dict[str, Any]:
    resp = TestClient(app).get(PATH, params={"skill": skill})
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture(scope="module")
def python_body() -> dict[str, Any]:
    return _get("python")


def _n(body: dict[str, Any], row: dict[str, Any]) -> int:
    """Cỡ mẫu của phép đo (không phải `n` của ô): `n_by_measure.skill_count`, thiếu thì `n`."""
    cell = body["meta"]["cells"][row["share"]["cell_id"]]
    return cell["n_by_measure"].get("skill_count", cell["n"])


def _share(value: float | None, display: str = "shown", cell_id: str = "vn.x.entry", kind: str = "skill_rate") -> Stat:
    return Stat(value=value, kind=kind, display=display, cell_id=cell_id)


def _row(role: str = "x", value: float | None = 0.5, display: str = "shown", **override: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"role": role, "share": _share(value, display, cell_id=f"vn.{role}.entry")}
    row.update(override)
    return row


def _data(rows: list[dict[str, Any]], **override: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"skill": SKILL, "level": "entry", "levels": ENTRY_LEVELS, "mentioned": True, "rows": rows}
    data.update(override)
    return data


# ---------------------------------------------------------------- hình (AC 1 của #166)


def test_fr09_dong_hop_le() -> None:
    row = SkillRoleRow.model_validate(_row())
    assert row.share.kind is MeasureKind.SKILL_RATE


@pytest.mark.parametrize(
    ("override", "match"),
    [
        ({"share": _share(0.5, kind="level_share", cell_id="vn.x.entry")}, "skill_rate"),
        ({"share": _share(0.5, cell_id="vn.y.entry")}, "cell_id"),
        ({"share": _share(0.5, cell_id="vn.x")}, "cell_id"),
        ({"share": _share(0.5, cell_id="ha_noi.x.entry")}, "cell_id"),
    ],
)
def test_fr09_dong_sai_la_loi(override: dict[str, Any], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        SkillRoleRow.model_validate(_row(**override))


def test_fr09_skill_rate_duoi_nguong_khong_duoc_hien_mo() -> None:
    with pytest.raises(ValidationError, match="low_sample_shown"):
        _share(0.5, display="low_sample_shown")


def test_fr09_data_hop_le_voi_dong_null_data_o_cuoi() -> None:
    rows = [_row("a", 0.5), _row("b", 0.2), _row("c", None, "null_data")]
    data = SkillRolesData.model_validate(_data(rows))
    assert [r.role for r in data.rows] == ["a", "b", "c"]


@pytest.mark.parametrize(
    ("rows", "override", "match"),
    [
        ([_row("a"), _row("a")], {}, "trùng"),
        ([], {}, "rows"),
        ([_row()], {"levels": []}, "levels"),
        ([_row("a", 0.2), _row("b", 0.5)], {}, "thứ tự"),
        ([_row("b", 0.5), _row("a", 0.5)], {}, "thứ tự"),
        ([_row("a", None, "null_data"), _row("b", 0.5)], {}, "thứ tự"),
        ([_row("a", 0.5)], {"mentioned": False}, "mentioned"),
    ],
    ids=["role_lap", "rong", "levels_rong", "tang_dan", "hoa_sai_ma", "null_data_truoc", "mentioned_sai"],
)
def test_fr09_data_sai_la_loi(rows: list[dict[str, Any]], override: dict[str, Any], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        SkillRolesData.model_validate(_data(rows, **override))


def test_fr09_khong_ai_nhac_thi_mentioned_false_van_co_dong_0_va_null_data() -> None:
    rows = [_row("a", 0.0), _row("b", 0.0), _row("c", None, "null_data")]
    data = SkillRolesData.model_validate(_data(rows, mentioned=False))
    assert data.mentioned is False


def test_fr09_ty_le_duong_o_dong_hien_thi_thi_mentioned_phai_true() -> None:
    with pytest.raises(ValidationError, match="mentioned"):
        SkillRolesData.model_validate(_data([_row("a", 0.1)], mentioned=False))
    # mentioned = true mà mọi dòng hiện là 0 là hợp lệ: tin nhắc nằm ở ô dưới ngưỡng bị ẩn
    SkillRolesData.model_validate(_data([_row("a", 0.0), _row("c", None, "null_data")], mentioned=True))


def test_fr09_mentioned_false_voi_dong_pha_tron_0_va_duong_la_loi() -> None:
    """Chỉ cần một dòng dương là mâu thuẫn: không được nhầm `any` thành `all`."""
    rows = [_row("a", 0.5), _row("b", 0.0), _row("c", None, "null_data")]
    with pytest.raises(ValidationError, match="mentioned"):
        SkillRolesData.model_validate(_data(rows, mentioned=False))
    with pytest.raises(ValidationError, match="mentioned"):
        SkillRolesData.model_validate(_data([_row("a", 0.0), _row("b", 0.5)][::-1], mentioned=False))


def test_fr09_level_la_ma_nhom_entry_va_ho_so_ky_nang_nhan_duoc() -> None:
    """`data.level` để #169 mở `/ho-so-ky-nang?role=&level=entry` (#111): mã phải nằm trong `level_options` của config."""
    assert "entry" in load_rules().level_options
    assert "entry" in load_rules().level_groups
    with pytest.raises(ValidationError, match="level"):
        SkillRolesData.model_validate(_data([_row()], level="senior"))
    with pytest.raises(ValidationError, match="level"):
        SkillRolesData.model_validate({k: v for k, v in _data([_row()]).items() if k != "level"})
    labels = (ROOT / "web" / "lib" / "labels.ts").read_text(encoding="utf-8")
    assert 'code: "entry"' in labels


def test_fr09_route_tra_hinh_va_nhan_ky_nang(python_body: dict[str, Any]) -> None:
    assert set(python_body) == {"data", "meta"}
    data = python_body["data"]
    assert set(data) == {"skill", "level", "levels", "mentioned", "rows"}
    assert data["level"] == "entry"
    assert data["skill"] == SKILL
    assert data["levels"] == ENTRY_LEVELS == list(load_rules().level_groups["entry"])
    assert data["mentioned"] is True
    min_sample = python_body["meta"]["thresholds"]["min_sample"]
    for row in data["rows"]:
        assert set(row) == {"role", "share"}
        share = row["share"]
        assert share["kind"] == "skill_rate"
        assert share["cell_id"] == f"vn.{row['role']}.entry"
        n = _n(python_body, row)
        assert share["display"] == suppression_for(MeasureKind.SKILL_RATE, n, min_sample=min_sample)
        assert (share["value"] is None) == (share["display"] == "null_data")


def test_fr09_nhan_ky_nang_la_ten_trong_bo_tu_vung() -> None:
    by_code = {s.code: s for s in load_seed_skills()}
    for code in ("python", "figma", "abap"):
        skill = _get(code)["data"]["skill"]
        assert skill == {"code": code, "name_en": by_code[code].name_en, "name_vi": by_code[code].name_vi}


def test_fr09_meta_co_dung_o_entry_cua_tung_dong(python_body: dict[str, Any]) -> None:
    cells = python_body["meta"]["cells"]
    assert set(cells) == {row["share"]["cell_id"] for row in python_body["data"]["rows"]}
    assert python_body["meta"]["thresholds"]["min_sample"] == 30
    assert python_body["meta"]["coverage_notes"]


# ---------------------------------------------------------------- dữ liệu giả (AC 2 của #166)


def test_fr09_gia_co_du_vai_tro_cua_config(python_body: dict[str, Any]) -> None:
    roles = [row["role"] for row in python_body["data"]["rows"]]
    assert len(roles) == len(set(roles))
    assert set(roles) == set(load_rules().roles)


def _scanned(role: str) -> int:
    """Cỡ mẫu của phép đo kỹ năng của ô entry của vai trò: `n_by_measure.skill_count` (= `n_scanned` của #101)."""
    cell = RAW["cells"][f"vn.{role}.entry"]
    return cell["n_by_measure"]["skill_count"]


def test_fr09_gia_fixture_dung_cac_vai_tro_cua_config_va_co_o_entry_cho_moi_vai_tro() -> None:
    """Chốt chống lệch: thêm hay bớt vai trò trong `config/rules.toml` mà quên fixture là test đỏ ở đây, không phải KeyError."""
    roles = set(load_rules().roles)
    for skill, entry in RAW["skill_roles"].items():
        assert set(entry) == {"entry", "mentions_all_levels"}, skill
        assert set(entry["entry"]) == roles, skill
        for role in roles:
            assert f"vn.{role}.entry" in RAW["cells"], (skill, role)


def test_fr09_gia_so_nhac_khong_vuot_cho_mau_cua_phep_do() -> None:
    for skill, entry in RAW["skill_roles"].items():
        for role, n_with in entry["entry"].items():
            assert isinstance(n_with, int)
            assert 0 <= n_with <= _scanned(role) <= RAW["cells"][f"vn.{role}.entry"]["n"], (skill, role)
        # số tin nhắc kỹ năng ở mọi cấp không nhỏ hơn tổng ở entry-level của mọi vai trò (mỗi tin một vai trò)
        assert entry["mentions_all_levels"] >= sum(entry["entry"].values()), skill


def test_fr09_gia_ma_ky_nang_co_trong_bo_tu_vung() -> None:
    vocab = {s.code for s in load_seed_skills()}
    assert set(RAW["skill_roles"]) <= vocab


@pytest.mark.parametrize("skill", sorted(RAW["skill_roles"]))
def test_fr09_gia_ty_le_bang_so_nhac_chia_cho_mau_cua_phep_do(skill: str) -> None:
    body = _get(skill)
    for row in body["data"]["rows"]:
        scanned = _n(body, row)
        n_with = RAW["skill_roles"][skill]["entry"][row["role"]]
        share = row["share"]
        if share["display"] == "shown":
            assert share["value"] == pytest.approx(n_with / scanned), (skill, row["role"])
        else:
            assert share["value"] is None
            assert scanned < 30


def test_fr09_gia_python_co_du_cac_truong_hop(python_body: dict[str, Any]) -> None:
    cases: dict[str, int] = {"shown_duong": 0, "duoi_30": 0, "shown_bang_0": 0}
    for row in python_body["data"]["rows"]:
        share, n = row["share"], _n(python_body, row)
        if share["display"] == "shown" and share["value"] > 0:
            cases["shown_duong"] += 1
        if share["display"] == "shown" and share["value"] == 0:
            assert n >= 30
            cases["shown_bang_0"] += 1
        if share["display"] == "null_data":
            cases["duoi_30"] += 1
    assert cases["shown_duong"] >= 5
    assert cases["duoi_30"] >= 2
    assert cases["shown_bang_0"] >= 1


def test_fr09_gia_ky_nang_thu_hai_xep_hang_khac_python(python_body: dict[str, Any]) -> None:
    other = _get("figma")
    top = lambda b: next(r["role"] for r in b["data"]["rows"] if r["share"]["display"] == "shown")
    assert top(python_body) != top(other)
    assert [r["role"] for r in python_body["data"]["rows"]] != [r["role"] for r in other["data"]["rows"]]
    # vai trò có tỷ lệ cao nhất thật sự (ui_ux) nằm dưới ngưỡng nên bị ẩn, không dẫn đầu
    hidden = {r["role"]: r["share"]["display"] for r in other["data"]["rows"]}
    assert hidden["ui_ux"] == "null_data"
    assert RAW["skill_roles"]["figma"]["entry"]["ui_ux"] / _scanned("ui_ux") > 0.5


def test_fr09_gia_ky_nang_khong_tin_nao_nhac_o_bat_ky_cap_nao() -> None:
    body = _get("abap")
    assert body["data"]["mentioned"] is False
    assert RAW["skill_roles"]["abap"]["mentions_all_levels"] == 0
    assert all(n == 0 for n in RAW["skill_roles"]["abap"]["entry"].values())
    shown = [r for r in body["data"]["rows"] if r["share"]["display"] == "shown"]
    assert shown
    assert all(r["share"]["value"] == 0 for r in shown)
    assert any(r["share"]["display"] == "null_data" for r in body["data"]["rows"])


def test_fr09_mentioned_theo_ac4_cua_113_la_moi_cap_khong_chi_entry() -> None:
    """AC 4 của #113: "kỹ năng mà không tin hiện tại nào nhắc" là không tin nào, ở cấp nào, nhắc. `sap` không có tin
    entry-level nào nhắc nhưng có tin ở cấp khác: `mentioned = true`, mọi dòng 0 hoặc ẩn."""
    body = _get("sap")
    assert all(n == 0 for n in RAW["skill_roles"]["sap"]["entry"].values())
    assert RAW["skill_roles"]["sap"]["mentions_all_levels"] > 0
    assert body["data"]["mentioned"] is True
    assert all(r["share"]["value"] in (0, None) for r in body["data"]["rows"])
    assert any(r["share"]["display"] == "shown" for r in body["data"]["rows"])


def _write(tmp_path: Path, raw: dict[str, Any]) -> Path:
    tmp = tmp_path / "fake_market.json"
    tmp.write_text(json.dumps(raw), encoding="utf-8")
    return tmp


def test_fr09_mentioned_chi_theo_so_nhac_moi_cap(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["skill_roles"]["abap"]["mentions_all_levels"] = 1
    assert FakeMarket(_write(tmp_path, raw)).skill_roles(skill="abap").data.mentioned is True
    raw["skill_roles"]["python"]["mentions_all_levels"] = 0
    raw["skill_roles"]["python"]["entry"] = {r: 0 for r in raw["skill_roles"]["python"]["entry"]}
    assert FakeMarket(_write(tmp_path, raw)).skill_roles(skill="python").data.mentioned is False


def test_fr09_gia_nhan_ky_nang_song_ngu_khac_nhau() -> None:
    """Một kỹ năng có tên tiếng Việt khác tiếng Anh (#167 dùng "học máy"): nhãn không đổi chỗ hai tên."""
    skill = _get("machine_learning")["data"]["skill"]
    assert skill == {"code": "machine_learning", "name_en": "Machine Learning", "name_vi": "Học máy"}


# ---------------------------------------------------------------- cỡ mẫu của phép đo (#166, 2026-11-17)


GAME = "game"  # n của ô = 43 nhưng chỉ 12 tin được quét kỹ năng


def test_fr09_n_cua_o_va_n_cua_phep_do_la_hai_so_khac_nhau(python_body: dict[str, Any]) -> None:
    row = next(r for r in python_body["data"]["rows"] if r["role"] == GAME)
    cell = python_body["meta"]["cells"]["vn.game.entry"]
    assert cell["n"] == 43  # cùng ô với newcomer-roles: n không đổi
    assert cell["n_by_measure"]["skill_count"] == 12
    assert cell["insufficient_by_measure"]["skill_count"] is True
    assert row["share"]["display"] == "null_data"  # 43 >= 30 nhưng 12 < 30
    assert _n(python_body, row) == 12


def test_fr09_o_entry_co_mot_n_duy_nhat_giua_newcomer_roles_va_skill_roles(python_body: dict[str, Any]) -> None:
    newcomer = TestClient(app).get("/api/v1/newcomer-roles").json()
    for role in load_rules().roles:
        cell_id = f"vn.{role}.entry"
        assert newcomer["meta"]["cells"][cell_id]["n"] == python_body["meta"]["cells"][cell_id]["n"]


def test_fr09_envelope_kiem_display_theo_n_cua_phep_do() -> None:
    """Envelope từ chối tỷ lệ `shown` khi `skill_count` dưới ngưỡng dù `n` của ô đủ mẫu."""
    body = FakeMarket().skill_roles(skill="python").model_dump(mode="json")
    game_row = next(r for r in body["data"]["rows"] if r["role"] == GAME)
    game_row["share"].update(value=0.1, display="shown")
    rows = body["data"]["rows"]
    shown = [r for r in rows if r["share"]["value"] is not None]
    hidden = [r for r in rows if r["share"]["value"] is None]
    shown.sort(key=lambda r: (-r["share"]["value"], r["role"]))  # giữ thứ tự hợp lệ; lỗi cần thấy là `display`
    body["data"]["rows"] = shown + hidden
    with pytest.raises(ValidationError, match="suppression_for"):
        Envelope[SkillRolesData].model_validate(body)


def test_fr09_dong_null_data_theo_n_cua_phep_do_roi_ma_vai_tro() -> None:
    """Dòng `null_data` xếp theo cỡ mẫu của phép đo giảm dần rồi mã vai trò. Xếp theo `n` của ô thì `game` (43) đứng đầu;
    theo `skill_count` thì `ui_ux` (21) đứng trước `game` (12)."""
    body = _get("python")
    hidden = [(_n(body, r), r["role"]) for r in body["data"]["rows"] if r["share"]["display"] == "null_data"]
    assert hidden == sorted(hidden, key=lambda t: (-t[0], t[1]))
    assert hidden[:2] == [(21, "ui_ux"), (12, GAME)]


def test_fr09_schema_kiem_thu_tu_null_data_theo_n_cua_phep_do() -> None:
    body = _get("python")
    hidden = [r for r in body["data"]["rows"] if r["share"]["display"] == "null_data"]
    assert len(hidden) >= 3

    def swap(roles: tuple[str, str]) -> dict[str, Any]:
        copy = json.loads(json.dumps(body))
        rows = copy["data"]["rows"]
        i, j = (next(k for k, r in enumerate(rows) if r["role"] == role) for role in roles)
        rows[i], rows[j] = rows[j], rows[i]
        return copy

    with pytest.raises(ValidationError, match="null_data"):
        Envelope[SkillRolesData].model_validate(swap((hidden[0]["role"], hidden[1]["role"])))
    # cùng n thì theo mã vai trò: đảo hai dòng hòa n cũng là lỗi
    tie = [r["role"] for r in hidden if _n(body, r) == 0]
    assert len(tie) >= 2
    with pytest.raises(ValidationError, match="null_data"):
        Envelope[SkillRolesData].model_validate(swap((tie[0], tie[1])))
    Envelope[SkillRolesData].model_validate(body)


def test_fr09_cac_route_khac_khong_doi_cach_kiem_display() -> None:
    """Quy tắc cỡ mẫu mới chỉ cho `skill_rate`. Ở bản giả `skill_count` của mọi ô bằng `n`, trừ `vn.game.entry`; ô đó vẫn
    cho `city-shares` và `newcomer-roles` (composition_share, level_share xét `n`) trả 200."""
    client = TestClient(app)
    assert client.get("/api/v1/newcomer-roles").status_code == 200
    assert client.get("/api/v1/city-shares", params={"role": "game", "level": "entry"}).status_code == 200
    assert client.get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"}).status_code == 200
    for cell_id, cell in RAW["cells"].items():
        skill_count = cell["n_by_measure"].get("skill_count")
        if skill_count is not None and cell_id != "vn.game.entry":
            assert skill_count == cell["n"], cell_id
    game = client.get("/api/v1/newcomer-roles").json()["data"]["rows"]
    assert next(r for r in game if r["role"] == GAME)["share"]["display"] == "shown"


def test_fr09_fake_loader_bao_loi_ro_khi_fixture_lech_config(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    del raw["skill_roles"]["python"]["entry"]["game"]
    with pytest.raises(ValueError, match=r"skill_roles\[python\].*game"):
        FakeMarket(_write(tmp_path, raw))
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["skill_roles"]["figma"]["entry"]["vai_tro_cu"] = 1
    with pytest.raises(ValueError, match=r"skill_roles\[figma\].*vai_tro_cu"):
        FakeMarket(_write(tmp_path, raw))
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    del raw["cells"]["vn.game.entry"]
    with pytest.raises(ValueError, match=r"vn\.game\.entry"):
        FakeMarket(_write(tmp_path, raw))


# ---------------------------------------------------------------- thứ tự do máy chủ quyết


@pytest.mark.parametrize("skill", sorted(RAW["skill_roles"]))
def test_fr09_thu_tu_dong_do_may_chu_quyet(skill: str) -> None:
    body = _get(skill)
    rows = body["data"]["rows"]

    def key(row: dict[str, Any]) -> tuple[Any, ...]:
        share = row["share"]
        if share["display"] == "null_data":
            return (1, 0.0, -_n(body, row), row["role"])
        return (0, -share["value"], 0, row["role"])

    assert [r["role"] for r in rows] == [r["role"] for r in sorted(rows, key=key)]
    displays = [r["share"]["display"] for r in rows]
    assert displays.index("null_data") > max(i for i, d in enumerate(displays) if d == "shown")


def test_fr09_thu_tu_hoa_theo_ma_vai_tro_va_null_data_theo_n_giam_dan() -> None:
    body = _get("figma")
    rows = body["data"]["rows"]
    zeros = [r["role"] for r in rows if r["share"]["display"] == "shown" and r["share"]["value"] == 0]
    assert len(zeros) >= 3
    assert zeros == sorted(zeros)
    hidden = [(_n(body, r), r["role"]) for r in rows if r["share"]["display"] == "null_data"]
    assert [n for n, _ in hidden] == sorted((n for n, _ in hidden), reverse=True)
    assert len({n for n, _ in hidden}) < len(hidden)  # có hòa n để thử luật theo mã
    for n in {n for n, _ in hidden}:
        group = [r for m, r in hidden if m == n]
        assert group == sorted(group)


# ---------------------------------------------------------------- lỗi


def test_fr09_ma_dung_dinh_dang_nhung_khong_co_trong_bo_tu_vung_la_404_unknown_skill() -> None:
    resp = TestClient(app).get(PATH, params={"skill": "khong_co_ky_nang_nay"})
    assert resp.status_code == 404, resp.text
    error = resp.json()["error"]
    assert error["code"] == "unknown_skill"
    assert error["snapshot_date"] is None
    assert error["message"]
    assert "khong_co_ky_nang_nay" not in error["message"]


def test_fr09_ky_nang_trong_bo_tu_vung_nhung_ban_gia_chua_co_so_la_404_unknown_cell() -> None:
    resp = TestClient(app).get(PATH, params={"skill": "java"})
    assert resp.status_code == 404, resp.text
    error = resp.json()["error"]
    assert error["code"] == "unknown_cell"
    assert error["snapshot_date"] == "2026-11-03"


@pytest.mark.parametrize(
    "params",
    [{}, {"skill": ""}, {"skill": "Python"}, {"skill": "py thon"}, {"skill": "a" * 41}, {"skill": "python__x"}],
    ids=["thieu", "rong", "hoa", "khoang_trang", "dai_41", "hai_gach_duoi"],
)
def test_fr09_tham_so_skill_sai_la_422(params: dict[str, str]) -> None:
    resp = TestClient(app).get(PATH, params=params)
    assert resp.status_code == 422, resp.text
    error = resp.json()["error"]
    assert error["code"] == "invalid_query"
    assert "skill" in error["message"]
    assert "detail" not in resp.json()


# ---------------------------------------------------------------- DEC-6: số chỉ nằm trong Stat và meta


def _strings(node: Any, path: str = "data") -> Iterator[tuple[str, str]]:
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, f"{path}[{i}]")


@pytest.mark.parametrize("skill", sorted(RAW["skill_roles"]))
def test_fr09_dec6_khong_cau_hay_nhan_nao_co_chu_so(skill: str) -> None:
    """Chỉ tên công nghệ (`data.skill.name_en`, `name_vi`) được có chữ số (DEC-6, AD-8 miễn tên công nghệ); mọi chuỗi
    khác của `data` không có chữ số nào. Test chữ số của màn hình (#170) cũng phải bỏ hai tên đó, không bỏ gì thêm."""
    body = _get(skill)
    for path, text in _strings(body["data"]):
        if path in ("data.skill.name_en", "data.skill.name_vi"):
            continue
        assert not re.search(r"\d", text), (path, text)


def test_fr09_dec6_fixture_chi_co_so_dem() -> None:
    for entry in RAW["skill_roles"].values():
        counts = [*entry["entry"].values(), entry["mentions_all_levels"]]
        assert all(isinstance(v, int) and not isinstance(v, bool) for v in counts)


# ---------------------------------------------------------------- nguồn dữ liệu


def test_fr09_bien_moi_truong_chon_nguon() -> None:
    assert SOURCE_ENV["skill_roles"] == "HAIDO_MARKET_SOURCE_SKILL_ROLES"
    sources = load_sources({})
    assert isinstance(sources["skill_roles"], FakeMarket)
    assert isinstance(load_sources({SOURCE_ENV["skill_roles"]: "stat"})["skill_roles"], StatMarket)
    with pytest.raises(ValueError, match="HAIDO_MARKET_SOURCE_SKILL_ROLES"):
        load_sources({SOURCE_ENV["skill_roles"]: "postgres"})


def test_fr09_thieu_nguon_skill_roles_la_loi_khoi_dong() -> None:
    sources = {op: FakeMarket() for op in SOURCE_ENV if op != "skill_roles"}
    with pytest.raises(ValueError, match="skill_roles"):
        create_app(sources)


def test_fr09_stat_khong_mo_ket_noi_luc_dung_nguon() -> None:
    """Từ #168 `StatMarket.skill_roles` đọc số thật (`test_fr09_skill_roles_stat.py`); kết nối chỉ mở ở yêu cầu đầu.

    Chưa có snapshot đọc được thì 404 `unknown_cell` không ngày (kiểm trên Postgres ở file đó), không bao giờ số giả.
    """

    class Opened(Exception):
        pass

    calls: list[int] = []

    def factory() -> Any:
        calls.append(1)
        raise Opened

    market = StatMarket(engine_factory=factory)
    assert calls == []  # dựng nguồn không mở kết nối
    with pytest.raises(Opened):
        market.skill_roles(skill="python")
    assert calls == [1]  # yêu cầu đầu tiên mở đúng một lần


def test_fr09_stat_ma_ngoai_bo_tu_vung_la_unknown_skill_truoc_khi_mo_ket_noi() -> None:
    calls: list[int] = []

    def factory() -> Any:
        calls.append(1)
        raise AssertionError("mã ngoài bộ từ vựng không được mở kết nối")

    market = StatMarket(engine_factory=factory)
    with pytest.raises(UnknownSkill):
        market.skill_roles(skill="khong_co_ky_nang")
    assert calls == []


def test_fr09_nguon_tra_sai_hop_dong_thanh_500() -> None:
    class _Bad:
        def skill_roles(self, *, skill: str) -> Any:
            return {"data": {"skill": SKILL, "levels": [], "mentioned": True, "rows": []}}

    sources = {op: FakeMarket() for op in SOURCE_ENV} | {"skill_roles": _Bad()}
    resp = TestClient(create_app(sources), raise_server_exceptions=False).get(PATH, params={"skill": "python"})
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "invalid_response"


def test_fr09_nguong_doc_tu_fixture(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["snapshot"]["thresholds"]["min_sample"] = 100
    fixture = tmp_path / "fake_market.json"
    fixture.write_text(json.dumps(raw), encoding="utf-8")
    env = FakeMarket(fixture).skill_roles(skill="python")
    by_role = {r.role: r.share.display for r in env.data.rows}
    assert by_role["backend"] is DisplayState.NULL_DATA  # n = 52
    assert by_role["ai_ml"] is DisplayState.SHOWN  # n = 501
