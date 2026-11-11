"""FR-22, FR-23, AD-17, AD-22 — hình response của lộ trình học (#212) và dữ liệu giả của nó.

Lộ trình trả về đã xếp sẵn (AD-7); `have` chỉ đổi cờ và các số đếm, không đổi thứ tự (AD-22).
"""

import copy
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from haido_api.fake_market import FakeMarket
from haido_api.main import app, create_app
from haido_api.market_source import UnknownCell
from haido_api.schemas.learning_path import LearningPathData
from haido_core.config import load_rules
from haido_core.vocab.skills import MAX_PROFILE_SKILLS, is_skill_code, load_seed_skills

PATH = "/api/v1/learning-path"
ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "haido_api" / "fixtures"
GROUP_RANK = {"core": 0, "common": 1, "company_specific": 2, None: 3}
CELL = "vn.x"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, **params: str) -> dict[str, Any]:
    resp = client.get(PATH, params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture(scope="module")
def backend(client: TestClient) -> dict[str, Any]:
    return _get(client, role="backend", level="entry")


def _skills(body: dict[str, Any]) -> Iterator[tuple[int, dict[str, Any]]]:
    for stage in body["data"]["stages"]:
        for skill in stage["skills"]:
            yield stage["stage"], skill


def _codes(body: dict[str, Any]) -> list[str]:
    return [s["skill"] for _, s in _skills(body)]


def _descendants(body: dict[str, Any], code: str) -> set[str]:
    """Mọi kỹ năng đi tới được từ `code` qua các cạnh `prerequisite_for` (bắc cầu)."""
    direct = {s["skill"]: s["prerequisite_for"] for _, s in _skills(body)}
    seen: set[str] = set()
    todo = list(direct[code])
    while todo:
        nxt = todo.pop()
        if nxt not in seen:
            seen.add(nxt)
            todo.extend(direct[nxt])
    return seen


def _assert_invariants(body: dict[str, Any], role: str) -> None:
    """Điều kiện mọi response 200 phải giữ (FR-19, FR-20, FR-22, AD-17)."""
    data, cells = body["data"], body["meta"]["cells"]
    assert data["role"] == role
    assert data["entry_cell_id"] in cells
    assert data["entry_cell_id"].split(".")[1] == role
    if data["status"] == "not_ready":
        assert data["stages"] == [] and data["cell_id"] is None
        return
    assert data["cell_id"] in cells
    assert data["cell_id"].split(".")[1] == role, "FR-19: quay về chỉ đi trong vai trò"
    assert set(cells) == {data["cell_id"], data["entry_cell_id"]}
    skills = [s for _, s in _skills(body)]
    by_code = {s["skill"]: s for s in skills}
    assert len(by_code) == len(skills) == data["path_size"]
    for skill in skills:
        assert skill["rate"]["cell_id"] == data["cell_id"]
        if skill["group"] == "company_specific":
            assert skill["foundation_for"], (
                f"{skill['skill']}: riêng công ty mà không phải nền tảng"
            )
        for target in skill["foundation_for"]:
            assert target in _descendants(body, skill["skill"])
            assert by_code[target]["group"] in ("core", "common")
        assert set(skill["prerequisite_for"]) <= set(by_code)


# ---------------------------------------------------------------- hình và thứ tự (FR-22)


def test_fr22_hinh_response_backend(backend: dict[str, Any]) -> None:
    data = backend["data"]
    assert set(data) == {
        "role", "level", "status", "cell_id", "entry_cell_id", "stages",
        "current_stage", "have_on_path", "path_size", "have_ignored",
    }  # fmt: skip
    assert (data["role"], data["level"], data["status"]) == (
        "backend",
        "entry",
        "ready",
    )
    assert [s["stage"] for s in data["stages"]] == list(
        range(1, len(data["stages"]) + 1)
    )
    assert len(data["stages"]) >= 3
    assert 12 <= data["path_size"] <= 16
    for _, skill in _skills(backend):
        assert set(skill) == {
            "skill", "rate", "group", "foundation_for", "prerequisite_for", "have", "blurb", "resource",
        }  # fmt: skip
        assert skill["rate"]["kind"] == "skill_rate"
        assert skill["rate"]["cell_id"] == data["cell_id"]
        assert set(skill["resource"]) == {"title", "url"}
        assert skill["resource"]["url"].startswith("https://")


def test_fr22_thu_tu_trong_chang_theo_khoa_fr22(backend: dict[str, Any]) -> None:
    for stage in backend["data"]["stages"]:
        keys = [
            (GROUP_RANK[s["group"]], -(s["rate"]["value"] or 0), s["skill"])
            for s in stage["skills"]
        ]
        assert keys == sorted(keys), f"chặng {stage['stage']} sai thứ tự"


def test_fr22_mot_chang_co_ca_cot_loi_va_thuong_gap(backend: dict[str, Any]) -> None:
    mixed = [
        st
        for st in backend["data"]["stages"]
        if {"core", "common"} <= {s["group"] for s in st["skills"]}
    ]
    assert mixed


def test_fr22_khong_ky_nang_nao_dung_truoc_to_tien(backend: dict[str, Any]) -> None:
    stage_of = {s["skill"]: stage for stage, s in _skills(backend)}
    for stage, skill in _skills(backend):
        for later in skill["prerequisite_for"]:
            assert stage_of[later] > stage, f"{skill['skill']} phải đứng trước {later}"


def test_fr20_ky_nang_nen_tang_va_nhom_rieng_cong_ty(backend: dict[str, Any]) -> None:
    foundations = [s for _, s in _skills(backend) if s["foundation_for"]]
    assert foundations
    for _, skill in _skills(backend):
        if skill["group"] == "company_specific":
            assert skill["foundation_for"], (
                f"{skill['skill']} riêng công ty mà không phải nền tảng"
            )
        for target in skill["foundation_for"]:
            assert target in _descendants(backend, skill["skill"])


def test_fr22_nhom_theo_theta(backend: dict[str, Any]) -> None:
    th = backend["meta"]["thresholds"]
    for _, skill in _skills(backend):
        value = skill["rate"]["value"]
        want = (
            "core"
            if value >= th["theta_core"]
            else "common"
            if value >= th["theta_common"]
            else "company_specific"
        )
        assert skill["group"] == want, skill["skill"]


# ---------------------------------------------------------------- khớp skill-rates (story #121)


@pytest.mark.parametrize(
    ("role", "level"),
    [("backend", "entry"), ("backend", "intern"), ("data_engineer", "entry")],
)
def test_fr22_ty_le_cua_lo_trinh_bang_skill_rates(
    client: TestClient, role: str, level: str
) -> None:
    path = _get(client, role=role, level=level)
    rates = _get_rates(client, role, level)
    assert path["data"]["cell_id"] == rates["data"]["cell_id"]
    by_skill = {r["skill"]: r for r in rates["data"]["rows"]}
    for _, skill in _skills(path):
        row = by_skill[skill["skill"]]
        assert skill["rate"] == row["rate"]
        assert skill["group"] == row["group"]


def _get_rates(client: TestClient, role: str, level: str) -> dict[str, Any]:
    resp = client.get("/api/v1/skill-rates", params={"role": role, "level": level})
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------- have (AD-22)


def test_ad22_have_dat_co_va_dem(client: TestClient, backend: dict[str, Any]) -> None:
    body = _get(client, role="backend", level="entry", have="java,sql")
    flags = {s["skill"]: s["have"] for _, s in _skills(body)}
    assert [c for c, v in flags.items() if v] == [
        c for c in _codes(body) if c in {"java", "sql"}
    ]
    assert body["data"]["have_on_path"] == 2
    assert body["data"]["path_size"] == backend["data"]["path_size"]
    assert body["data"]["have_ignored"] == []
    assert not any(s["have"] for _, s in _skills(backend))


def test_ad22_have_khong_doi_thu_tu_hay_chang(
    client: TestClient, backend: dict[str, Any]
) -> None:
    body = _get(client, role="backend", level="entry", have="java,git,spring_boot")
    assert [(st, s["skill"]) for st, s in _skills(body)] == [
        (st, s["skill"]) for st, s in _skills(backend)
    ]


def test_ad22_current_stage_la_chang_dau_con_ky_nang_chua_co(
    client: TestClient, backend: dict[str, Any]
) -> None:
    assert backend["data"]["current_stage"] == 1
    stage1 = [s["skill"] for s in backend["data"]["stages"][0]["skills"]]
    body = _get(client, role="backend", level="entry", have=",".join(stage1))
    assert body["data"]["current_stage"] == 2
    everything = ",".join(_codes(backend))
    done = _get(client, role="backend", level="entry", have=everything)
    assert done["data"]["current_stage"] is None
    assert done["data"]["have_on_path"] == done["data"]["path_size"]


def test_ad22_ma_ngoai_lo_trinh_vao_have_ignored_va_trung_chi_tinh_mot_lan(
    client: TestClient,
) -> None:
    body = _get(client, role="backend", level="entry", have="kafka,java,java,aws,java")
    assert body["data"]["have_ignored"] == ["aws", "kafka"]
    assert body["data"]["have_on_path"] == 1


def test_ad22_have_rong_nhu_khong_gui(
    client: TestClient, backend: dict[str, Any]
) -> None:
    assert _get(client, role="backend", level="entry", have="") == backend


def test_ad22_tran_200_ma(client: TestClient) -> None:
    ok = ",".join(f"skill_{i}" for i in range(MAX_PROFILE_SKILLS))
    resp = client.get(PATH, params={"role": "backend", "level": "entry", "have": ok})
    assert resp.status_code == 200
    resp = client.get(
        PATH, params={"role": "backend", "level": "entry", "have": ok + ",skill_x"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"
    assert "have" in resp.json()["error"]["message"]


@pytest.mark.parametrize(
    "have", ["Java", "spring-boot", "java,,sql", "java,", "a" * 41, "java sql", "_java"]
)
def test_ad22_ma_sai_dinh_dang_la_422(client: TestClient, have: str) -> None:
    resp = client.get(PATH, params={"role": "backend", "level": "entry", "have": have})
    assert resp.status_code == 422, resp.text
    assert resp.json()["error"]["code"] == "invalid_query"


def test_ad22_mac_dinh_cap_la_entry(
    client: TestClient, backend: dict[str, Any]
) -> None:
    assert _get(client, role="backend") == backend


# ---------------------------------------------------------------- not_ready, quay về, 404


def test_fr22_vai_tro_chua_co_lo_trinh_la_not_ready(client: TestClient) -> None:
    body = _get(client, role="qa", level="entry", have="java")
    data = body["data"]
    assert data["status"] == "not_ready"
    assert data["stages"] == []
    assert data["current_stage"] is None
    assert (data["have_on_path"], data["path_size"]) == (0, 0)
    assert data["cell_id"] is None
    assert data["have_ignored"] == ["java"]
    assert data["entry_cell_id"] == "vn.qa.entry"
    assert body["meta"]["cells"][data["entry_cell_id"]]["n"] == 82
    assert body["meta"]["coverage_notes"]


def test_fr22_not_ready_o_moi_cap_hop_le(client: TestClient) -> None:
    body = _get(client, role="ai_ml", level="senior")
    assert body["data"]["status"] == "not_ready"
    assert body["data"]["entry_cell_id"] == "vn.ai_ml.entry"


def test_fr19_data_engineer_entry_khong_o_nao_trong_vai_tro_du_30_thi_ty_le_la_null_data(
    client: TestClient,
) -> None:
    """FR-19: quay về chỉ đi trong vai trò (vai trò × cấp, rồi vai trò × mọi cấp); không có ô nào đủ 30 thì "chưa đủ dữ liệu"."""
    body = _get(client, role="data_engineer", level="entry")
    data, cells = body["data"], body["meta"]["cells"]
    min_sample = body["meta"]["thresholds"]["min_sample"]
    assert data["status"] == "ready"
    assert data["entry_cell_id"] == "vn.data_engineer.entry"
    assert data["cell_id"] == "vn.data_engineer"
    assert cells[data["entry_cell_id"]]["n"] == 4 < min_sample
    assert cells[data["cell_id"]]["n"] == 22 < min_sample
    assert cells[data["entry_cell_id"]]["fallback_label"] is None
    label = cells[data["cell_id"]]["fallback_label"]
    assert label
    assert "4" in label and "22" in label and "30" in label
    assert "Data Engineer" in label and "Entry" in label
    skills = [s for _, s in _skills(body)]
    assert skills
    for skill in skills:
        assert skill["rate"]["display"] == "null_data"
        assert skill["rate"]["value"] is None
        assert skill["group"] is None
        assert skill["foundation_for"] == []
    for stage in data["stages"]:
        codes = [s["skill"] for s in stage["skills"]]
        assert codes == sorted(codes), (
            "nhóm null cùng bậc: xếp theo mã A–Z, không lộ xếp hạng của tỷ lệ đã ẩn"
        )


def test_fr19_backend_intern_quay_ve_vai_tro_moi_cap_va_nhan_ghi_ty_le_mid_tro_len(
    client: TestClient,
) -> None:
    """Bước cuối của FR-19: ô vai trò × mọi cấp đủ mẫu; nhãn ghi tỷ lệ tin Mid trở lên, lấy từ chính `seniority_mix`."""
    body = _get(client, role="backend", level="intern")
    data, cells = body["data"], body["meta"]["cells"]
    assert data["status"] == "ready"
    assert data["cell_id"] == "vn.backend"
    assert data["entry_cell_id"] == "vn.backend.entry"
    cell = cells[data["cell_id"]]
    assert cell["n"] >= body["meta"]["thresholds"]["min_sample"]
    mix = cell["seniority_mix"]
    assert sum(mix.values()) == cell["n"]
    mid_up = sum(
        count for level, count in mix.items() if level in {"mid", "senior", "lead"}
    )
    percent = round(100 * mid_up / cell["n"])
    label = cell["fallback_label"]
    assert label
    assert f"{mid_up}" in label and f"{cell['n']}" in label and f"{percent}%" in label
    assert str(mix["intern"]) in label
    assert all(s["rate"]["display"] == "shown" for _, s in _skills(body))
    assert all(s["rate"]["cell_id"] == "vn.backend" for _, s in _skills(body))


def test_ad17_backend_khong_quay_ve_va_du_mau(backend: dict[str, Any]) -> None:
    cells = backend["meta"]["cells"]
    assert backend["data"]["cell_id"] == backend["data"]["entry_cell_id"]
    assert set(cells) == {backend["data"]["cell_id"]}
    assert cells[backend["data"]["cell_id"]]["n"] >= 30
    assert cells[backend["data"]["cell_id"]]["fallback_label"] is None


def test_ad17_cap_khac_cua_vai_tro_san_sang_la_404_nhu_skill_rates(
    client: TestClient,
) -> None:
    for level in ("senior", "all"):
        resp = client.get(PATH, params={"role": "backend", "level": level})
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "unknown_cell"


@pytest.mark.parametrize(
    "params", [{"role": "khong_ton_tai"}, {"role": "all"}, {"role": "java_backend"}]
)
def test_ad17_vai_tro_la_404(client: TestClient, params: dict[str, str]) -> None:
    resp = client.get(PATH, params=params)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


@pytest.mark.parametrize(
    "params", [{}, {"role": "backend", "level": "khong_ton_tai"}, {"role": "Back-End"}]
)
def test_ad17_tham_so_sai_la_422(client: TestClient, params: dict[str, str]) -> None:
    resp = client.get(PATH, params=params)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"


# ---------------------------------------------------------------- tất định


@pytest.mark.determinism
def test_fr22_cung_yeu_cau_hai_lan_cho_cung_body(client: TestClient) -> None:
    for params in (
        {"role": "backend", "level": "entry", "have": "sql,java,git"},
        {"role": "data_engineer", "level": "entry"},
        {"role": "qa", "level": "entry"},
    ):
        first = client.get(PATH, params=params)
        second = client.get(PATH, params=params)
        assert first.content == second.content
    fresh = TestClient(create_app())
    assert (
        fresh.get(PATH, params={"role": "backend"}).content
        == client.get(PATH, params={"role": "backend"}).content
    )


# ---------------------------------------------------------------- dữ liệu giả


def test_fr22_vai_tro_cua_du_lieu_gia_khop_config(client: TestClient) -> None:
    ready = {"backend", "data_engineer"}
    for role in load_rules().roles:
        status = _get(client, role=role, level="entry")["data"]["status"]
        assert status == ("ready" if role in ready else "not_ready"), role


def test_fr22_ma_ky_nang_gia_deu_thuoc_danh_sach_moi_va_snake_case(
    client: TestClient,
) -> None:
    seed = {s.code for s in load_seed_skills()}
    raw_market = json.loads((FIXTURES / "fake_market.json").read_text(encoding="utf-8"))
    codes = {
        row["skill"]
        for levels in raw_market["skill_rates"].values()
        for entry in levels.values()
        for row in entry["rows"]
    }
    raw_path = json.loads(
        (FIXTURES / "fake_learning_path.json").read_text(encoding="utf-8")
    )
    codes |= {s["skill"] for role in raw_path["roles"].values() for s in role["skills"]}
    for role in ("backend", "data_engineer"):
        codes |= set(_codes(_get(client, role=role, level="entry")))
    assert codes
    assert all(is_skill_code(c) for c in codes), sorted(
        c for c in codes if not is_skill_code(c)
    )
    assert codes <= seed, sorted(codes - seed)


def test_fr23_loi_dan_khong_khuyen_bo_qua_ky_nang() -> None:
    raw = (FIXTURES / "fake_learning_path.json").read_text(encoding="utf-8").lower()
    for banned in ("đừng học", "bỏ qua", "không cần học"):
        assert banned not in raw


def test_fr23_moi_tai_nguyen_la_link_https_khong_trung_ky_nang(
    client: TestClient,
) -> None:
    body = _get(client, role="backend", level="entry")
    for _, skill in _skills(body):
        assert re.fullmatch(r"https://[^\s]+", skill["resource"]["url"])
        assert skill["resource"]["title"].strip()


# ---------------------------------------------------------------- nguồn


def test_ad17_fake_nem_unknown_cell_co_ngay_snapshot() -> None:
    with pytest.raises(UnknownCell) as info:
        FakeMarket().learning_path(role="khong_ton_tai", level="entry", have=())
    assert info.value.snapshot_date is not None


def test_ad17_stat_market_chua_co_so_that_nen_la_unknown_cell() -> None:
    from haido_api.stat_market import StatMarket

    with pytest.raises(UnknownCell):
        StatMarket(
            engine_factory=lambda: (_ for _ in ()).throw(
                AssertionError("không mở kết nối")
            )
        ).learning_path(role="backend", level="entry", have=())


# ---------------------------------------------------------------- validator của schema


def _stat(
    value: float | None = 0.5, cell_id: str = CELL, display: str = "shown"
) -> dict[str, Any]:
    return {
        "value": value,
        "kind": "skill_rate",
        "display": display,
        "cell_id": cell_id,
    }


def _skill(
    code: str,
    value: float | None = 0.5,
    group: str | None = "core",
    *,
    prereq: tuple[str, ...] = (),
    foundation: tuple[str, ...] = (),
    have: bool = False,
    cell_id: str = CELL,
) -> dict[str, Any]:
    display = "null_data" if value is None else "shown"
    return {
        "skill": code,
        "rate": _stat(value, cell_id, display),
        "group": group,
        "foundation_for": list(foundation),
        "prerequisite_for": list(prereq),
        "have": have,
        "blurb": "Một câu.",
        "resource": {"title": "Tài liệu", "url": "https://example.org/x"},
    }


def _data(**override: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "role": "backend",
        "level": "entry",
        "status": "ready",
        "cell_id": CELL,
        "entry_cell_id": CELL,
        "stages": [
            {
                "stage": 1,
                "skills": [
                    _skill("java", 0.7, prereq=("spring_boot",)),
                    _skill("sql", 0.6),
                ],
            },
            {"stage": 2, "skills": [_skill("spring_boot", 0.5)]},
        ],
        "current_stage": 1,
        "have_on_path": 0,
        "path_size": 3,
        "have_ignored": [],
    }
    data.update(override)
    return data


def test_fr22_schema_nhan_du_lieu_dung() -> None:
    parsed = LearningPathData.model_validate(_data())
    assert parsed.path_size == 3


def _with_stages(*stages: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "stages": [{"stage": i, "skills": s} for i, s in enumerate(stages, start=1)],
        "path_size": sum(len(s) for s in stages),
    }
    return _data(**(base | extra))


def _mutated(path: str, value: Any) -> dict[str, Any]:
    data = copy.deepcopy(_data())
    node: Any = data
    *head, last = path.split(".")
    for part in head:
        node = node[int(part)] if part.isdigit() else node[part]
    node[int(last) if last.isdigit() else last] = value
    return data


BROKEN: list[tuple[str, dict[str, Any], str]] = [
    (
        "rate khác ô",
        _mutated("stages.0.skills.0.rate", _stat(0.7, "vn.khac")),
        "cell_id",
    ),
    ("chặng không liền", _mutated("stages.1.stage", 3), "stage"),
    (
        "chặng bắt đầu từ 0",
        _with_stages([_skill("java", 0.7)])
        | {"stages": [{"stage": 0, "skills": [_skill("java")]}]},
        "stage",
    ),
    ("chặng rỗng", _with_stages([_skill("java", 0.7)], [], path_size=1), "skills"),
    (
        "sai thứ tự tỷ lệ",
        _with_stages([_skill("sql", 0.3), _skill("java", 0.7)], current_stage=1),
        "thứ tự",
    ),
    (
        "thường gặp trước cốt lõi",
        _with_stages([_skill("java", 0.2, "common"), _skill("sql", 0.1, "core")]),
        "thứ tự",
    ),
    (
        "sai thứ tự mã",
        _with_stages([_skill("sql", 0.5), _skill("java", 0.5)]),
        "thứ tự",
    ),
    ("mã lặp", _with_stages([_skill("java", 0.7)], [_skill("java", 0.5)]), "lặp"),
    ("mã sai định dạng", _with_stages([_skill("Spring-Boot", 0.7)]), "Mã"),
    (
        "prerequisite_for không có trên lộ trình",
        _with_stages([_skill("java", 0.7, prereq=("go",))]),
        "go",
    ),
    (
        "foundation_for không có trên lộ trình",
        _with_stages([_skill("java", 0.7, foundation=("go",))]),
        "go",
    ),
    (
        "đứng trước ở cùng chặng",
        _with_stages([_skill("java", 0.7, prereq=("sql",)), _skill("sql", 0.6)]),
        "chặng",
    ),
    (
        "đứng sau kỹ năng cần nó",
        _with_stages([_skill("sql", 0.6)], [_skill("java", 0.7, prereq=("sql",))]),
        "chặng",
    ),
    (
        "riêng công ty mà không phải nền tảng",
        _with_stages([_skill("java", 0.05, "company_specific")]),
        "nền tảng",
    ),
    (
        "nền tảng không nằm trong prerequisite_for",
        _with_stages([_skill("java", 0.7, foundation=("sql",))], [_skill("sql", 0.6)]),
        "foundation_for",
    ),
    ("group null mà có giá trị", _with_stages([_skill("java", 0.7, None)]), "group"),
    ("have_on_path sai", _mutated("have_on_path", 2), "have_on_path"),
    ("path_size sai", _mutated("path_size", 9), "path_size"),
    ("current_stage sai", _mutated("current_stage", 2), "current_stage"),
    (
        "current_stage phải null khi đã có hết",
        _with_stages([_skill("java", 0.7, have=True)], have_on_path=1, current_stage=1),
        "current_stage",
    ),
    (
        "have_ignored không xếp",
        _mutated("have_ignored", ["sql_x", "aws"]),
        "have_ignored",
    ),
    (
        "have_ignored trùng ma trên lộ trình",
        _mutated("have_ignored", ["java"]),
        "have_ignored",
    ),
    ("not_ready mà có chặng", _mutated("status", "not_ready"), "not_ready"),
    (
        "ready mà không có chặng",
        _data(stages=[], path_size=0, current_stage=None),
        "ready",
    ),
    ("ready mà cell_id null", _mutated("cell_id", None), "cell_id"),
    (
        "not_ready mà có cell_id",
        _data(status="not_ready", stages=[], current_stage=None, path_size=0),
        "cell_id",
    ),
    (
        "not_ready mà có đếm",
        _data(
            status="not_ready", stages=[], current_stage=None, cell_id=None, path_size=1
        ),
        "path_size",
    ),
    ("lời dẫn rỗng", _mutated("stages.0.skills.0.blurb", ""), "blurb"),
    (
        "link không https",
        _mutated("stages.0.skills.0.resource.url", "http://example.org"),
        "url",
    ),
    ("trường lạ", _mutated("extra", 1), "extra"),
]


@pytest.mark.parametrize(("name", "data", "match"), BROKEN, ids=[b[0] for b in BROKEN])
def test_fr22_validator_tu_choi_du_lieu_sai(
    name: str, data: dict[str, Any], match: str
) -> None:
    with pytest.raises(ValidationError, match=match):
        LearningPathData.model_validate(data)


def test_fr22_not_ready_hop_le() -> None:
    parsed = LearningPathData.model_validate(
        _data(
            status="not_ready",
            stages=[],
            current_stage=None,
            cell_id=None,
            path_size=0,
            have_ignored=["java"],
        )
    )
    assert parsed.stages == []


def test_fr22_ky_nang_nen_tang_co_the_la_nhom_rieng_cong_ty() -> None:
    data = _with_stages(
        [
            _skill("java", 0.7),
            _skill(
                "linux",
                0.05,
                "company_specific",
                prereq=("docker",),
                foundation=("docker",),
            ),
        ],
        [_skill("docker", 0.2, "common")],
    )
    assert LearningPathData.model_validate(data).path_size == 3


def test_fr22_rate_null_data_thi_group_null_va_xep_cuoi() -> None:
    data = _with_stages([_skill("java", 0.7), _skill("sql", None, None)])
    assert LearningPathData.model_validate(data).stages[0].skills[1].group is None
