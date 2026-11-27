"""FR-20, FR-22, AD-7, AD-17 — lộ trình học thật (#216): chỉ lộ trình đã rà soát được hiện, tỷ lệ bằng `skill-rates`.

Nội dung (chủ đề, đồ thị, lời dẫn) ở `haido_api/content/learning_path.json`; vai trò có `review = null` là `not_ready` (#96).
"""

import copy
import json
from collections.abc import Iterator
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_api.stat_path import DRAFT_NOTE, PATH_FILE, Review, RolePath, load_paths
from haido_core.config import load_rules
from tests.api.test_fr19_skill_rates_stat import _cell, _snapshot
from tests.steps.conftest import S

ROOT = Path(__file__).resolve().parents[2]
RULES = load_rules()
REVIEW = Review(reviewed_on=date(2026, 11, 25), record="docs/x.md")
CONTENT = load_paths()
REVIEWED = {role: replace(path, review=REVIEW) for role, path in CONTENT.items()}
UNREVIEWED = {role: replace(path, review=None) for role, path in CONTENT.items()}
ALL_BACKEND = dict.fromkeys(CONTENT["backend"].nodes, 30)


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


def _client(engine: Engine, paths: dict[str, RolePath]) -> TestClient:
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: engine, rules=RULES, paths=paths)
    app = create_app(
        {"city_shares": fake, "skill_rates": stat, "newcomer_roles": fake, "learning_path": stat, "skill_roles": fake, "posting_check": fake}
    )
    return TestClient(app, raise_server_exceptions=False)


def _call(client: TestClient, role: str = "backend", level: str = "entry", **extra: str):
    return client.get("/api/v1/learning-path", params={"role": role, "level": level} | extra)


def _ok(client: TestClient, role: str = "backend", level: str = "entry", **extra: str) -> dict[str, Any]:
    resp = _call(client, role, level, **extra)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _good(engine: Engine) -> None:
    _snapshot(engine)
    _cell(engine, "backend", "entry", 80, 60, ALL_BACKEND | {"java": 36, "sql": 12})
    _cell(engine, "backend", "all", 500, 400, dict.fromkeys(ALL_BACKEND, 200))


# ---------------------------------------------------------------- AC 2: chưa rà soát là not_ready


@pytest.mark.parametrize("level", ["entry", "senior", "all"])
def test_fr22_ac2_vai_tro_chua_ra_soat_la_not_ready_o_moi_cap(pg_engine: Engine, level: str) -> None:
    _good(pg_engine)
    body = _ok(_client(pg_engine, UNREVIEWED), level=level, have="java,git")
    data, meta = body["data"], body["meta"]
    assert data["status"] == "not_ready" and data["stages"] == []
    assert data["cell_id"] is None and data["current_stage"] is None
    assert (data["have_on_path"], data["path_size"]) == (0, 0)
    assert data["have_ignored"] == ["git", "java"]
    assert data["entry_cell_id"] == "vn.backend.entry"
    assert set(meta["cells"]) == {"vn.backend.entry"} and meta["cells"]["vn.backend.entry"]["n"] == 80
    assert meta["snapshot_date"] == S and meta["sources"] == ["itviec", "zalo"]
    assert DRAFT_NOTE.code not in {n["code"] for n in meta["coverage_notes"]}


def test_fr22_ac2_vai_tro_khong_co_noi_dung_hay_khong_co_tin_van_la_not_ready(pg_engine: Engine) -> None:
    _good(pg_engine)
    body = _ok(_client(pg_engine, REVIEWED), role="frontend")
    assert body["data"]["status"] == "not_ready"
    assert body["meta"]["cells"]["vn.frontend.entry"]["n"] == 0


def test_fr22_ac2_mac_dinh_dung_noi_dung_cua_repo(pg_engine: Engine) -> None:
    _good(pg_engine)
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    app = create_app(
        {"city_shares": fake, "skill_rates": stat, "newcomer_roles": fake, "learning_path": stat, "skill_roles": fake, "posting_check": fake}
    )
    want = "ready" if CONTENT["backend"].review else "not_ready"
    assert _ok(TestClient(app))["data"]["status"] == want


@pytest.mark.parametrize("role", ["khong_co", "all"])
def test_ad17_vai_tro_la_la_404_kem_ngay(pg_engine: Engine, role: str) -> None:
    _good(pg_engine)
    resp = _call(_client(pg_engine, REVIEWED), role=role)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell" and resp.json()["error"]["snapshot_date"] == S


@pytest.mark.parametrize("paths", [REVIEWED, UNREVIEWED])
def test_ad17_chua_co_snapshot_la_404_khong_ngay(pg_engine: Engine, paths: dict[str, RolePath]) -> None:
    resp = _call(_client(pg_engine, paths))
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell" and resp.json()["error"]["snapshot_date"] is None


# ---------------------------------------------------------------- AC 1: lộ trình đã rà soát


def test_fr22_ac1_da_ra_soat_thi_ready_va_ty_le_bang_skill_rates_cung_snapshot(pg_engine: Engine) -> None:
    _good(pg_engine)
    client = _client(pg_engine, REVIEWED)
    body = _ok(client)
    rates = client.get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"}).json()
    assert body["data"]["status"] == "ready"
    assert body["data"]["cell_id"] == rates["data"]["cell_id"] == "vn.backend.entry"
    assert body["meta"]["snapshot_date"] == rates["meta"]["snapshot_date"] == S
    assert body["meta"]["coverage_notes"] == rates["meta"]["coverage_notes"], "đã rà soát thì không có lưu ý bản nháp"
    got = {k["skill"]: (k["rate"], k["group"]) for st in body["data"]["stages"] for k in st["skills"]}
    assert got == {r["skill"]: (r["rate"], r["group"]) for r in rates["data"]["rows"]}


def test_fr22_ac1_cot_loi_truoc_thuong_gap_trong_chang(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, dict.fromkeys(ALL_BACKEND, 12) | {"python": 40, "jira": 30})
    for stage in _ok(_client(pg_engine, REVIEWED))["data"]["stages"]:
        groups = [k["group"] for k in stage["skills"]]
        assert groups == sorted(groups, key=["core", "common", "company_specific"].index)


def test_ad7_chi_doc_bang_stat_va_snapshots(pg_engine: Engine, statements: list[str]) -> None:
    _good(pg_engine)
    statements.clear()
    _ok(_client(pg_engine, REVIEWED))
    assert statements
    for sql in statements:
        assert "haido.job_" not in sql and "GROUP BY" not in sql.upper() and "COUNT(" not in sql.upper()


# ---------------------------------------------------------------- nội dung và dấu rà soát (#96)


def _raw() -> dict[str, Any]:
    return json.loads(PATH_FILE.read_text(encoding="utf-8"))


def _load(tmp_path: Path, raw: dict[str, Any]) -> dict[str, RolePath]:
    file = tmp_path / "p.json"
    file.write_text(json.dumps(raw), encoding="utf-8")
    return load_paths(file)


def test_gh96_doc_dau_ra_soat(tmp_path: Path) -> None:
    raw = _raw()
    raw["roles"]["backend"]["review"] = {"reviewed_on": "2026-12-01", "record": "docs/data/ra-soat.md"}
    raw["roles"]["data_engineer"]["review"] = None
    paths = _load(tmp_path, raw)
    assert paths["backend"].review == Review(date(2026, 12, 1), "docs/data/ra-soat.md")
    assert paths["data_engineer"].review is None


@pytest.mark.parametrize(
    "review",
    [
        "thiếu",
        True,
        {},
        {"reviewed_on": "2026-12-01"},
        {"reviewed_on": "hôm qua", "record": "docs/x.md"},
        {"reviewed_on": "2026-12-01", "record": " "},
        {"reviewed_on": "2026-12-01", "record": "docs/x.md", "by": "ai đó"},
    ],
)
def test_gh96_dau_ra_soat_sai_la_loi_khong_thanh_da_ra_soat(tmp_path: Path, review: object) -> None:
    raw = copy.deepcopy(_raw())
    if review == "thiếu":
        del raw["roles"]["backend"]["review"]
    else:
        raw["roles"]["backend"]["review"] = review
    with pytest.raises(ValueError, match="backend"):
        _load(tmp_path, raw)


def test_gh96_lo_trinh_da_ra_soat_phai_co_bien_ban_trong_repo() -> None:
    for role, path in CONTENT.items():
        if path.review is not None:
            assert path.review.record.startswith("docs/"), role
            assert (ROOT / path.review.record).is_file(), f"{role}: thiếu biên bản {path.review.record}"


def test_gh96_do_thi_hong_la_loi_luc_nap(tmp_path: Path) -> None:
    raw = _raw()
    raw["roles"]["backend"]["skills"][0]["requires"] = ["khong_co"]
    with pytest.raises(ValueError, match="khong_co"):
        _load(tmp_path, raw)
