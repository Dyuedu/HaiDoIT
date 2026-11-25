"""FR-20, FR-22, AD-7, AD-17 — lộ trình nháp ghép tỷ lệ thật của snapshot với đồ thị chưa rà soát (#216, một phần).

Nguồn `draft` chỉ để demo trên máy: đồ thị là `fixtures/fake_learning_path.json`, tỷ lệ và nhóm là của `skill-rates` thật.
"""

import json

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from haido_api.draft_path import DRAFT_FIXTURE, DRAFT_NOTE_CODE, DraftPathMarket
from haido_api.fake_market import FakeMarket
from haido_core.vocab.skills import load_seed_skills
from haido_api.learning_path import Topic, topic_stages
from haido_api.main import create_app
from haido_api.routes.market import IMPLEMENTATIONS, SOURCE_ENV, load_sources
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.vocab.prepared_text import prepared_text_problems
from tests.api.test_fr19_skill_rates_stat import _cell, _snapshot
from tests.api.test_fr23_blurbs import FREQUENCY_CLAIMS
from tests.steps.conftest import S

RULES = load_rules()
ROOT_DEPLOY = Path(__file__).resolve().parents[2] / "deploy"
GRAPH = {
    role: {n["skill"]: n["requires"] for n in entry["skills"]}
    for role, entry in json.loads(DRAFT_FIXTURE.read_text(encoding="utf-8"))["roles"].items()
}
ALL_BACKEND = dict.fromkeys(GRAPH["backend"], 30)


def _client(engine: Engine) -> TestClient:
    fake = FakeMarket()
    draft = DraftPathMarket(engine_factory=lambda: engine, rules=RULES)
    app = create_app(
        {"city_shares": fake, "skill_rates": draft, "newcomer_roles": fake, "learning_path": draft, "skill_roles": fake}
    )
    return TestClient(app, raise_server_exceptions=False)


def _get(engine: Engine, role: str = "backend", have: str | None = None) -> dict:
    params = {"role": role, "level": "entry"} | ({"have": have} if have else {})
    resp = _client(engine).get("/api/v1/learning-path", params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _skills(body: dict) -> dict[str, dict]:
    return {s["skill"]: s | {"stage": st["stage"]} for st in body["data"]["stages"] for s in st["skills"]}


def test_fr22_ty_le_va_nhom_bang_skill_rates_cung_o(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND | {"java": 36, "sql": 12})
    body = _get(pg_engine)
    rates = _client(pg_engine).get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"}).json()
    assert body["data"]["status"] == "ready"
    assert body["data"]["cell_id"] == rates["data"]["cell_id"] == "vn.backend.entry"
    assert body["meta"]["snapshot_date"] == rates["meta"]["snapshot_date"] == S
    want = {r["skill"]: (r["rate"], r["group"]) for r in rates["data"]["rows"]}
    got = {code: (s["rate"], s["group"]) for code, s in _skills(body).items()}
    assert got == want and set(got) == set(GRAPH["backend"])


def test_fr22_canh_cua_do_thi_luon_tang_chang(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND)
    skills = _skills(_get(pg_engine))
    for code, needs in GRAPH["backend"].items():
        assert all(skills[need]["stage"] < skills[code]["stage"] for need in needs)


def test_fr20_hiem_khong_la_to_tien_bi_bo_hiem_la_to_tien_thanh_nen_tang(pg_engine: Engine) -> None:
    # linux hiếm nhưng docker cần nó: giữ, ghi nền tảng. nodejs hiếm và không ai cần: bỏ.
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND | {"linux": 1, "nodejs": 1})
    skills = _skills(_get(pg_engine))
    assert "nodejs" not in skills
    assert skills["linux"]["group"] == "company_specific"
    assert skills["linux"]["rate"]["value"] == pytest.approx(1 / 60)
    assert "docker" in skills["linux"]["foundation_for"]


def test_fr19_quay_ve_o_rong_hon_giu_nhan_va_o_entry(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 22, 22, dict.fromkeys(ALL_BACKEND, 10))
    _cell(pg_engine, "backend", "all", 500, 400, dict.fromkeys(ALL_BACKEND, 200))
    body = _get(pg_engine)
    assert body["data"]["cell_id"] == "vn.backend"
    assert body["data"]["entry_cell_id"] == "vn.backend.entry"
    assert body["meta"]["cells"]["vn.backend"]["fallback_label"]
    assert body["meta"]["cells"]["vn.backend.entry"]["n"] == 22


def test_fr19_khong_o_nao_du_mau_thi_moi_ty_le_bi_an(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "all", 10, 10, dict.fromkeys(ALL_BACKEND, 5))
    skills = _skills(_get(pg_engine))
    assert set(skills) == set(GRAPH["backend"])
    assert all(s["rate"]["value"] is None and s["group"] is None and s["foundation_for"] == [] for s in skills.values())


def test_ad22_have_chi_doi_co_va_so_dem(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND)
    body = _get(pg_engine, have="java,figma")
    assert _skills(body)["java"]["have"] is True
    assert body["data"]["have_on_path"] == 1 and body["data"]["have_ignored"] == ["figma"]


def test_fr22_vai_tro_chua_co_do_thi_la_not_ready_kem_so_tin_entry(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "frontend", "entry", 16, 16, {"html": 12})
    _cell(pg_engine, "frontend", "all", 100, 90, {"html": 60})
    body = _get(pg_engine, role="frontend")
    assert body["data"]["status"] == "not_ready" and body["data"]["stages"] == []
    assert body["meta"]["cells"]["vn.frontend.entry"]["n"] == 16
    assert DRAFT_NOTE_CODE not in {n["code"] for n in body["meta"]["coverage_notes"]}  # không có lộ trình để gọi là nháp


def test_fr22_luu_y_noi_ro_ban_nhap(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND)
    body = _get(pg_engine)
    notes = {n["code"]: n["text"] for n in body["meta"]["coverage_notes"]}
    assert "chưa được giảng viên rà soát" in notes[DRAFT_NOTE_CODE]
    rates = _client(pg_engine).get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"}).json()
    assert DRAFT_NOTE_CODE not in {n["code"] for n in rates["meta"]["coverage_notes"]}


def test_fr22_chua_co_snapshot_thi_404(pg_engine: Engine) -> None:
    resp = _client(pg_engine).get("/api/v1/learning-path", params={"role": "backend", "level": "entry"})
    assert resp.status_code == 404 and resp.json()["error"]["code"] == "unknown_cell"


def test_gh309_ban_nhap_chi_chay_bang_compose_demo() -> None:
    def api(name: str) -> dict:
        return yaml.safe_load((ROOT_DEPLOY / name).read_text(encoding="utf-8"))["services"]["api"]

    demo = api("compose.demo.yml")
    assert "haido_api.demo:app" in demo["command"]
    assert {demo["environment"][var] for var in SOURCE_ENV.values()} == {"stat"}
    assert "command" not in api("compose.prod.yml") and "command" not in api("compose.local.yml")
    assert "haido_api.main:app" in (ROOT_DEPLOY / "api.Dockerfile").read_text(encoding="utf-8")
    assert DraftPathMarket not in IMPLEMENTATIONS.values()
    assert type(load_sources({SOURCE_ENV["learning_path"]: "stat"})["learning_path"]) is StatMarket


def test_gh216_app_demo_dung_ban_nhap_cho_lo_trinh(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in SOURCE_ENV.values():
        monkeypatch.setenv(var, "stat")
    from haido_api import demo

    sources = demo.app.state.market_sources
    assert type(sources["learning_path"]) is DraftPathMarket
    assert set(sources) == set(SOURCE_ENV)


@pytest.mark.parametrize("role", sorted(GRAPH))
def test_fr22_do_thi_nhap_hop_le(role: str) -> None:
    raw = json.loads(DRAFT_FIXTURE.read_text(encoding="utf-8"))["roles"][role]
    topics = [Topic(t["title"], t["choose_one"], tuple(t["skills"])) for t in raw["topics"]]
    stages = topic_stages(topics, GRAPH[role])
    assert sum(len(s.skills) for s in stages) == len(GRAPH[role]) == len(raw["skills"])
    assert any(s.choose_one for s in stages)
    assert set(GRAPH[role]) <= {s.code for s in load_seed_skills()}


def test_fr23_loi_dan_nhap_dung_quy_tac() -> None:
    raw = json.loads(DRAFT_FIXTURE.read_text(encoding="utf-8"))
    for role, entry in raw["roles"].items():
        for topic in entry["topics"]:
            assert prepared_text_problems(topic["title"]) == [], topic["title"]
        for node in entry["skills"]:
            key = f"{role}.{node['skill']}"
            assert prepared_text_problems(node["blurb"]) == [], key
            assert prepared_text_problems(node["resource"]["title"]) == [], key
            assert node["resource"]["url"].startswith("https://"), key
            for phrase in (*FREQUENCY_CLAIMS, "đừng học", "bỏ qua", "không cần học"):
                assert phrase not in node["blurb"].casefold(), f"{key}: {phrase}"


def test_fr22_backend_chang_chon_mot_xong_khi_co_mot(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, ALL_BACKEND)
    stages = _get(pg_engine)["data"]["stages"]
    lang = next(s for s in stages if s["choose_one"])
    before = [k["skill"] for s in stages if s["stage"] < lang["stage"] for k in s["skills"]]
    body = _get(pg_engine, have=",".join([*before, "java"]))
    assert body["data"]["current_stage"] == lang["stage"] + 1
