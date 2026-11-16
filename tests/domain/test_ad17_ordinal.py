"""AD-17, AD-22 — dấu `Ordinal` chỉ miễn cho số thứ tự và số đếm trên chính response (#212, sửa sau review).

`Ordinal` bỏ qua kiểm "số đứng riêng ngoài Stat" khi kiểu của trường đúng là `Ordinal` hoặc `Ordinal | None` và giá
trị là `int` (không phải `bool`) không âm hoặc `None`. Kiểu ghép (tuple, union với kiểu khác) không được miễn.
"""

from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from haido_core.domain.envelope import CellId, Envelope, Ordinal, Stat, _walk


def _cell(n: int) -> dict[str, Any]:
    return {
        "n": n,
        "fallback_label": None,
        "seniority_mix": {"junior": n},
        "n_by_measure": {"skill_count": n},
        "insufficient_by_measure": {"skill_count": n < 30},
    }


def _meta() -> dict[str, Any]:
    return {
        "snapshot_date": "2026-11-03",
        "snapshot_status": "published",
        "sources": ["careerlink"],
        "sources_failed": [],
        "thresholds": {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1},
        "coverage_notes": [{"code": "n_sources", "text": "Chỉ gồm tin đăng online."}],
        "cells": {"vn.x": _cell(100)},
    }


def _stat(cell_id: str = "vn.x") -> dict[str, Any]:
    return {"value": 0.5, "kind": "skill_rate", "display": "shown", "cell_id": cell_id}


class _Plain(BaseModel):
    position: Ordinal
    maybe: Ordinal | None = None


class _Pair(BaseModel):
    pair: tuple[Ordinal, float]


class _Mixed(BaseModel):
    value: list[Stat] | Ordinal


def test_ad17_ordinal_int_duoc_nhan() -> None:
    env = Envelope[_Plain].model_validate(
        {"data": {"position": 3, "maybe": 0}, "meta": _meta()}
    )
    assert env.data.position == 3
    none_ok = Envelope[_Plain].model_validate(
        {"data": {"position": 0, "maybe": None}, "meta": _meta()}
    )
    assert none_ok.data.maybe is None


def test_ad17_ordinal_am_bi_tu_choi() -> None:
    with pytest.raises(ValidationError):
        Envelope[_Plain].model_validate({"data": {"position": -1}, "meta": _meta()})


def test_ad17_kieu_ghep_chua_ordinal_khong_duoc_mien_so_float() -> None:
    with pytest.raises(ValidationError, match="số đứng riêng ngoài Stat"):
        Envelope[_Pair].model_validate({"data": {"pair": (1, 0.5)}, "meta": _meta()})


def test_ad17_union_voi_ordinal_van_kiem_stat_trong_list() -> None:
    with pytest.raises(ValidationError, match="không có mục trong meta.cells"):
        Envelope[_Mixed].model_validate(
            {"data": {"value": [_stat("vn.khong_co")]}, "meta": _meta()}
        )
    ok = Envelope[_Mixed].model_validate(
        {"data": {"value": [_stat()]}, "meta": _meta()}
    )
    assert isinstance(ok.data.value, list)
    with pytest.raises(ValidationError, match="số đứng riêng ngoài Stat"):
        Envelope[_Mixed].model_validate({"data": {"value": 4}, "meta": _meta()})


def test_ad17_bool_khong_phai_ordinal() -> None:
    bad = _Plain.model_construct(position=True, maybe=None)
    assert [path for path, found in _walk(bad, "data") if found is None] == [
        "data.position"
    ]
    good = _Plain.model_construct(position=2, maybe=None)
    assert list(_walk(good, "data")) == []


def test_ad17_ordinal_am_qua_walk_cung_bi_chan() -> None:
    bad = _Plain.model_construct(position=-2, maybe=None)
    assert [path for path, found in _walk(bad, "data") if found is None] == [
        "data.position"
    ]


def test_ad17_ordinal_float_qua_walk_bi_chan() -> None:
    bad = _Plain.model_construct(position=1.5, maybe=None)
    assert [path for path, found in _walk(bad, "data") if found is None] == [
        "data.position"
    ]


class _CellHolder(BaseModel):
    cell: CellId
    position: Ordinal


def test_ad17_ordinal_khong_lam_mat_kiem_cell_id_o_truong_khac() -> None:
    with pytest.raises(ValidationError, match=r"data\.cell"):
        Envelope[_CellHolder].model_validate(
            {"data": {"cell": "vn.khong_co", "position": 1}, "meta": _meta()}
        )
