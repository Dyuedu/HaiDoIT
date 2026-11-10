"""#205 — `GET /api/v1/skills` trả danh sách kỹ năng mồi cho web."""

import numbers
from typing import Any

from fastapi.testclient import TestClient

from haido_api.main import app
from haido_core.vocab.skills import VOCAB_VERSION, load_seed_skills


def _numbers(node: Any) -> list[Any]:
    if isinstance(node, bool):
        return []
    if isinstance(node, numbers.Number):
        return [node]
    if isinstance(node, dict):
        return [n for v in node.values() for n in _numbers(v)]
    if isinstance(node, list):
        return [n for v in node for n in _numbers(v)]
    return []


def test_fr13_route_skills_tra_danh_sach_moi() -> None:
    resp = TestClient(app).get("/api/v1/skills")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body) == {"data"}
    assert body["data"]["vocab_version"] == VOCAB_VERSION
    rows = body["data"]["skills"]
    seed = load_seed_skills()
    assert [r["code"] for r in rows] == [s.code for s in seed]
    assert set(rows[0]) == {"code", "name_en", "name_vi", "aliases"}


def test_fr13_route_skills_khong_chua_so() -> None:
    body = TestClient(app).get("/api/v1/skills").json()
    assert _numbers(body) == []
