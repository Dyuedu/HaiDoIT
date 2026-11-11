"""FR-37, AD-17 — hình response của màn người mới (#144) và dữ liệu giả của nó.

Số tin entry-level là `meta.cells[entry_cell_id].n`, n của vai trò là `meta.cells[total_cell_id].n`,
tỷ lệ là `share` (`level_share`). Web không tính, không sắp xếp lại (AD-22).
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from haido_api.main import app
from haido_api.schemas.market import NewcomerRoleRow, NewcomerRolesData
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import Stat

PATH = "/api/v1/newcomer-roles"
ENTRY_LEVELS = ["intern", "fresher", "junior"]


@pytest.fixture(scope="module")
def body() -> dict[str, Any]:
    resp = TestClient(app).get(PATH)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _counts(body: dict[str, Any], row: dict[str, Any]) -> tuple[int, int]:
    cells = body["meta"]["cells"]
    return cells[row["entry_cell_id"]]["n"], cells[row["total_cell_id"]]["n"]


def _share(value: float | None, display: str = "shown", cell_id: str = "vn.x", kind: str = "level_share") -> Stat:
    return Stat(value=value, kind=kind, display=display, cell_id=cell_id)


def _row(**override: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "role": "x",
        "total_cell_id": "vn.x",
        "entry_cell_id": "vn.x.entry",
        "share": _share(0.5),
    }
    row.update(override)
    return row


# ---------------------------------------------------------------- hình (AC 1 của #144)


def test_fr37_level_share_duoi_nguong_la_null_data() -> None:
    assert suppression_for(MeasureKind.LEVEL_SHARE, 29, min_sample=30) is DisplayState.NULL_DATA
    assert suppression_for(MeasureKind.LEVEL_SHARE, 30, min_sample=30) is DisplayState.SHOWN


def test_fr37_level_share_khong_duoc_hien_mo_va_nam_trong_0_1() -> None:
    with pytest.raises(ValidationError, match="low_sample_shown"):
        _share(0.5, display="low_sample_shown")
    with pytest.raises(ValidationError, match="0–1"):
        _share(1.5)


def test_fr37_dong_hop_le() -> None:
    row = NewcomerRoleRow.model_validate(_row())
    data = NewcomerRolesData(levels=ENTRY_LEVELS, rows=[row])
    assert data.rows[0].share.kind is MeasureKind.LEVEL_SHARE


@pytest.mark.parametrize(
    ("override", "match"),
    [
        ({"share": _share(0.5, kind="composition_share")}, "level_share"),
        ({"share": _share(0.5, cell_id="vn.y")}, "total_cell_id"),
        ({"entry_cell_id": "vn.x"}, "entry_cell_id"),
    ],
)
def test_fr37_dong_sai_la_loi(override: dict[str, Any], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        NewcomerRoleRow.model_validate(_row(**override))


def test_fr37_vai_tro_lap_hoac_rong_la_loi() -> None:
    with pytest.raises(ValidationError, match="trùng"):
        NewcomerRolesData(levels=ENTRY_LEVELS, rows=[_row(), _row()])
    with pytest.raises(ValidationError):
        NewcomerRolesData(levels=ENTRY_LEVELS, rows=[])
    with pytest.raises(ValidationError):
        NewcomerRolesData(levels=[], rows=[_row()])


def test_fr37_route_tra_so_entry_ty_le_va_n(body: dict[str, Any]) -> None:
    assert set(body) == {"data", "meta"}
    assert body["data"]["levels"] == ENTRY_LEVELS
    min_sample = body["meta"]["thresholds"]["min_sample"]
    for row in body["data"]["rows"]:
        assert set(row) == {"role", "total_cell_id", "entry_cell_id", "share"}
        entry, n = _counts(body, row)
        share = row["share"]
        assert share["kind"] == "level_share"
        assert share["cell_id"] == row["total_cell_id"]
        assert share["display"] == suppression_for(MeasureKind.LEVEL_SHARE, n, min_sample=min_sample)
        assert 0 <= entry <= n


# ---------------------------------------------------------------- dữ liệu giả (AC 2 của #144)


def test_fr37_gia_co_du_vai_tro_cua_config(body: dict[str, Any]) -> None:
    roles = [row["role"] for row in body["data"]["rows"]]
    assert len(roles) == len(set(roles))
    assert set(roles) == set(load_rules().roles)


def test_fr37_gia_entry_bang_intern_fresher_junior_va_ty_le_khop(body: dict[str, Any]) -> None:
    cells = body["meta"]["cells"]
    for row in body["data"]["rows"]:
        mix = cells[row["total_cell_id"]]["seniority_mix"]
        entry, n = _counts(body, row)
        assert entry == sum(mix.get(level, 0) for level in ENTRY_LEVELS), row["role"]
        assert cells[row["entry_cell_id"]]["seniority_mix"] == {
            level: mix[level] for level in ENTRY_LEVELS if mix.get(level)
        }, row["role"]
        if row["share"]["display"] == "shown":
            assert row["share"]["value"] == pytest.approx(entry / n), row["role"]
        else:
            assert row["share"]["value"] is None


def test_fr37_gia_co_du_bon_truong_hop(body: dict[str, Any]) -> None:
    cases = set()
    for row in body["data"]["rows"]:
        entry, n = _counts(body, row)
        shown = row["share"]["display"] == "shown"
        if shown and entry > 0:
            cases.add("du_mau")
        if shown and entry == 0:
            cases.add("du_mau_khong_co_entry")
        if not shown and n > 0:
            cases.add("duoi_30")
        if n == 0:
            cases.add("khong_co_tin")
    assert cases == {"du_mau", "du_mau_khong_co_entry", "duoi_30", "khong_co_tin"}


def test_fr37_thu_tu_dong_do_may_chu_quyet(body: dict[str, Any]) -> None:
    rows = body["data"]["rows"]

    def key(row: dict[str, Any]) -> tuple[bool, int, str]:
        entry, _ = _counts(body, row)
        return (row["share"]["display"] == "null_data", -entry, row["role"])

    assert [r["role"] for r in rows] == [r["role"] for r in sorted(rows, key=key)]
    displays = [r["share"]["display"] for r in rows]
    assert displays.index("null_data") > displays.index("shown")
