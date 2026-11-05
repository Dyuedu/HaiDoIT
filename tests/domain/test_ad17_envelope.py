"""AD-17 — hợp đồng envelope `{data, meta}`. Dòng "Hợp đồng vỡ" của I/O Matrix và AC về import."""

import ast
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from haido_core.domain.envelope import (
    CellId,
    CellMeta,
    Envelope,
    Meta,
    Stat,
    Thresholds,
)

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "haido_core" / "domain"


class _Row(BaseModel):
    city: str
    share: Stat


class _Data(BaseModel):
    total_cell_id: CellId
    rows: list[_Row]
    by_key: dict[str, Stat] = {}


def _cell(n: int) -> dict[str, Any]:
    return {
        "n": n,
        "fallback_label": None,
        "seniority_mix": {"junior": n},
        "n_by_measure": {"skill_count": n, "salary": 0},
        "insufficient_by_measure": {"skill_count": n < 30, "salary": True},
    }


def _stat(value: float | None, display: str, cell_id: str, kind: str = "composition_share") -> dict:
    return {"value": value, "kind": kind, "display": display, "cell_id": cell_id}


def _hop_le() -> dict[str, Any]:
    return {
        "data": {
            "total_cell_id": "vn.data_ai",
            "rows": [
                {"city": "ha_noi", "share": _stat(0.9, "shown", "ha_noi.data_ai")},
                {"city": "da_nang", "share": _stat(0.1, "low_sample_shown", "da_nang.data_ai")},
            ],
        },
        "meta": {
            "snapshot_date": "2026-11-03",
            "snapshot_status": "published",
            "sources": ["careerlink", "itnavi"],
            "sources_failed": [],
            "thresholds": {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1},
            "coverage_notes": [{"code": "n_sources", "text": "Chỉ gồm tin đăng online."}],
            "cells": {
                "vn.data_ai": _cell(210),
                "ha_noi.data_ai": _cell(189),
                "da_nang.data_ai": _cell(21),
            },
        },
    }


def _validate(body: dict[str, Any]) -> Envelope[_Data]:
    return Envelope[_Data].model_validate(body)


def test_ad17_envelope_hop_le_qua_validator() -> None:
    env = _validate(_hop_le())
    dumped = env.model_dump(mode="json")
    assert dumped["meta"]["snapshot_date"] == "2026-11-03"
    assert dumped["data"]["rows"][1]["share"]["display"] == "low_sample_shown"
    assert set(dumped["meta"]) == {
        "snapshot_date", "snapshot_status", "sources", "sources_failed",
        "thresholds", "coverage_notes", "cells",
    }


def test_ad17_thieu_meta_la_loi_schema() -> None:
    body = _hop_le()
    del body["meta"]
    with pytest.raises(ValidationError, match="meta"):
        _validate(body)


def test_ad17_stat_tro_toi_o_khong_co_trong_meta_la_loi() -> None:
    body = _hop_le()
    del body["meta"]["cells"]["da_nang.data_ai"]
    with pytest.raises(ValidationError, match=r"data\.rows\[1\]\.share\.cell_id"):
        _validate(body)


def test_ad17_truong_cell_id_ngoai_stat_cung_phai_co_o() -> None:
    body = _hop_le()
    del body["meta"]["cells"]["vn.data_ai"]
    with pytest.raises(ValidationError, match=r"data\.total_cell_id"):
        _validate(body)


def test_ad17_stat_long_trong_dict_cung_duoc_kiem() -> None:
    body = _hop_le()
    body["data"]["by_key"] = {"x": _stat(0.5, "shown", "o_la")}
    with pytest.raises(ValidationError, match="o_la"):
        _validate(body)


def test_ad17_so_dung_rieng_trong_data_la_loi() -> None:
    class _CoSoDungRieng(BaseModel):
        total: int

    with pytest.raises(ValidationError, match="số đứng riêng"):
        Envelope[_CoSoDungRieng].model_validate({"data": {"total": 5}, "meta": _hop_le()["meta"]})


@pytest.mark.parametrize("kind", ["skill_rate", "percentile"])
def test_ad17_low_sample_shown_chi_cho_ty_trong_cau_phan(kind: str) -> None:
    with pytest.raises(ValidationError, match="low_sample_shown"):
        Stat.model_validate(_stat(0.4, "low_sample_shown", "o", kind=kind))


def test_ad17_null_data_ma_co_gia_tri_la_loi() -> None:
    with pytest.raises(ValidationError, match="null_data"):
        Stat.model_validate(_stat(0.4, "null_data", "o", kind="skill_rate"))


@pytest.mark.parametrize("display", ["shown", "low_sample_shown"])
def test_ad17_hien_ma_khong_co_gia_tri_la_loi(display: str) -> None:
    with pytest.raises(ValidationError, match="phải có giá trị"):
        Stat.model_validate(_stat(None, display, "o"))


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_ad17_ty_le_ngoai_0_1_la_loi(value: float) -> None:
    with pytest.raises(ValidationError, match="0–1"):
        Stat.model_validate(_stat(value, "shown", "o", kind="skill_rate"))


def test_ad17_phan_vi_khong_bi_gioi_han_0_1() -> None:
    stat = Stat.model_validate(_stat(25_000_000, "shown", "o", kind="percentile"))
    assert stat.value == 25_000_000


def test_ad17_ty_le_khong_bi_lam_tron() -> None:
    body = _hop_le()
    body["data"]["rows"][0]["share"]["value"] = 189 / 210
    body["data"]["rows"][1]["share"]["value"] = 21 / 210
    env = _validate(body)
    assert env.model_dump(mode="json")["data"]["rows"][0]["share"]["value"] == 189 / 210


def test_ad17_muc_o_phai_co_cung_tap_thuoc_do() -> None:
    cell = _cell(40)
    del cell["insufficient_by_measure"]["salary"]
    with pytest.raises(ValidationError, match="cùng tập thước đo"):
        CellMeta.model_validate(cell)


def test_ad17_n_cua_thuoc_do_khong_vuot_n_cua_o() -> None:
    cell = _cell(40)
    cell["n_by_measure"]["salary"] = 41
    with pytest.raises(ValidationError, match="vượt n"):
        CellMeta.model_validate(cell)


def test_ad17_published_khong_co_nguon_loi() -> None:
    meta = _hop_le()["meta"]
    meta["sources_failed"] = ["itnavi"]
    with pytest.raises(ValidationError, match="sources_failed"):
        Meta.model_validate(meta)
    meta["snapshot_status"] = "partial"
    assert Meta.model_validate(meta).sources_failed == ["itnavi"]


@pytest.mark.parametrize(
    ("path", "bad"),
    [
        (("meta", "snapshot_date"), "03/11/2026"),
        (("meta", "snapshot_status"), "draft"),
        (("meta", "thresholds", "min_sample"), 0),
        (("meta", "thresholds", "theta_core"), 1.5),
    ],
)
def test_ad17_truong_meta_sai_kieu_la_loi(path: tuple[str, ...], bad: object) -> None:
    body = _hop_le()
    target: Any = body
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = bad
    with pytest.raises(ValidationError):
        _validate(body)


def test_ad17_truong_la_bi_tu_choi() -> None:
    body = _hop_le()
    body["meta"]["stat_cell"] = "vn.data_ai"
    with pytest.raises(ValidationError, match="stat_cell"):
        _validate(body)


def test_ad17_display_lech_suppression_for_la_loi() -> None:
    body = _hop_le()
    body["meta"]["cells"]["o.n18"] = _cell(18)
    body["data"]["by_key"] = {"rate": _stat(0.5, "shown", "o.n18", kind="skill_rate")}
    with pytest.raises(ValidationError, match=r"data\.by_key\['rate'\]\.display = shown"):
        _validate(body)


@pytest.mark.parametrize(
    ("value", "display"), [(None, "null_data"), (0.1, "shown")], ids=["null_data", "shown"]
)
def test_ad17_ty_trong_mau_nho_phai_low_sample_shown(value: float | None, display: str) -> None:
    body = _hop_le()
    body["data"]["rows"][1]["share"] = _stat(value, display, "da_nang.data_ai")
    with pytest.raises(ValidationError, match="suppression_for cho low_sample_shown"):
        _validate(body)


def test_ad17_insufficient_lech_n_by_measure_la_loi() -> None:
    body = _hop_le()
    body["meta"]["cells"]["ha_noi.data_ai"]["insufficient_by_measure"]["salary"] = False
    with pytest.raises(ValidationError, match=r"insufficient_by_measure\['salary'\] phải là true"):
        _validate(body)


class _DataRefs(BaseModel):
    total_cell_id: CellId
    optional_cell_id: CellId | None = None
    cell_ids: list[CellId] = []
    by_city: dict[str, CellId] = {}


@pytest.mark.parametrize(
    ("field", "value", "path"),
    [
        ("optional_cell_id", "o_la", r"data\.optional_cell_id = 'o_la'"),
        ("cell_ids", ["vn.data_ai", "o_la"], r"data\.cell_ids\[1\] = 'o_la'"),
        ("by_city", {"ha_noi": "o_la"}, r"data\.by_city\['ha_noi'\] = 'o_la'"),
    ],
)
def test_ad17_cell_id_long_trong_optional_list_dict_cung_duoc_kiem(
    field: str, value: object, path: str
) -> None:
    meta = _hop_le()["meta"]
    ok = Envelope[_DataRefs].model_validate(
        {"data": {"total_cell_id": "vn.data_ai", "optional_cell_id": None}, "meta": meta}
    )
    assert ok.data.optional_cell_id is None
    with pytest.raises(ValidationError, match=path):
        Envelope[_DataRefs].model_validate(
            {"data": {"total_cell_id": "vn.data_ai", field: value}, "meta": meta}
        )


class _CoDecimal(BaseModel):
    total: Decimal


class _CoSet(BaseModel):
    sizes: frozenset[int]


@pytest.mark.parametrize(
    ("model", "data"),
    [(_CoDecimal, {"total": "5.5"}), (_CoSet, {"sizes": [3]})],
    ids=["decimal", "frozenset"],
)
def test_ad17_decimal_va_so_trong_set_cung_la_so_dung_rieng(
    model: type[BaseModel], data: dict
) -> None:
    with pytest.raises(ValidationError, match="số đứng riêng"):
        Envelope[model].model_validate({"data": data, "meta": _hop_le()["meta"]})


def test_ad17_meta_phai_co_luu_y_do_phu() -> None:
    meta = _hop_le()["meta"]
    meta["coverage_notes"] = []
    with pytest.raises(ValidationError, match="coverage_notes"):
        Meta.model_validate(meta)


def test_ad17_theta_common_khong_lon_hon_theta_core() -> None:
    with pytest.raises(ValidationError, match="theta_common không được lớn hơn theta_core"):
        Thresholds.model_validate({"min_sample": 30, "theta_core": 0.1, "theta_common": 0.3})


# ---------------------------------------------------------------- AC: import của domain


def _imported_modules(path: Path) -> set[str]:
    """Tên module mà file import; import tương đối trả về dạng `.ten`."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add("." * node.level + (node.module or ""))
    return names


def _is_stdlib(module: str) -> bool:
    return not module.startswith(".") and module.split(".")[0] in sys.stdlib_module_names


def test_ad17_display_policy_chi_import_thu_vien_chuan() -> None:
    modules = _imported_modules(DOMAIN / "display_policy.py")
    assert modules, "display_policy.py phải import enum"
    assert {m for m in modules if not _is_stdlib(m)} == set()


def test_ad17_envelope_chi_import_thu_vien_chuan_pydantic_va_display_policy() -> None:
    display_policy = {"haido_core.domain.display_policy", ".display_policy"}
    modules = _imported_modules(DOMAIN / "envelope.py")
    other = {
        m for m in modules
        if not _is_stdlib(m) and m.split(".")[0] != "pydantic" and m not in display_policy
    }
    assert other == set()
    assert modules & display_policy
