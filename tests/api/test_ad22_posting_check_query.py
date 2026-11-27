"""AD-22, AD-11 — query của `GET /api/v1/posting-check` chỉ có mã và số, không bao giờ có chữ của tin (#230)."""

import re
from typing import Any

import pytest
from fastapi.testclient import TestClient
from posting_samples import (
    BACKEND_TEXT,
    CLOUD_TEXT,
    FEE_TEXT,
    HAVE_16_OF_18,
    POSTING_SKILLS,
    SENTINEL,
    csv,
    query_from_read,
)

from haido_api.fake_market import FakeMarket
from haido_api.main import app, create_app
from haido_api.routes import market
from haido_api.schemas.posting import (
    MAX_SALARY,
    ContactChannel,
    PostingFacts,
    PostingSalary,
)
from haido_core.vocab.skills import MAX_PROFILE_SKILLS

URL = "/api/v1/posting-check"
BASE = {"role": "backend", "level": "junior", "skills": csv(POSTING_SKILLS)}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, **extra: str) -> Any:
    return client.get(URL, params={**BASE, **extra})


def _invalid(resp: Any) -> None:
    assert resp.status_code == 422, resp.text
    assert resp.json()["error"]["code"] == "invalid_query"
    assert SENTINEL not in resp.text


def test_ad22_day_du_su_kien_dong_la_hop_le(client: TestClient) -> None:
    resp = _get(
        client,
        have=csv(HAVE_16_OF_18),
        years_min="1",
        salary_min="10000000",
        salary_max="18000000",
        salary_currency="vnd",
        salary_period="month",
        company_named="true",
        contacts="company_email,zalo",
        fees="2",
        duties_described="true",
        title_level="junior",
        salary_non_numeric="false",
        collected_reposts="3",
        collected_snapshots="41",
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["match"]["level"]["percent"] == 89


def test_ad22_moi_su_kien_toi_duoc_nguon_nhu_da_gui(client: TestClient) -> None:
    """Route chuyển cho nguồn đúng các mã và số đã gửi (nguồn thật đọc chúng ở #240–#246)."""
    captured: dict[str, Any] = {}

    class _Spy(FakeMarket):
        def posting_check(self, **kwargs: Any) -> Any:
            captured.update(kwargs)
            return super().posting_check(**kwargs)

    spy_client = TestClient(create_app({name: _Spy() for name in market.SOURCE_ENV}))
    resp = spy_client.get(
        URL,
        params={
            "role": "devops", "level": "entry", "branch": "cloud", "skills": "docker,aws", "have": "docker",
            "years_min": "3", "salary_min": "1000", "salary_max": "1500", "salary_currency": "usd", "salary_period": "month",
            "company_named": "true", "contacts": "company_email,zalo", "fees": "2", "duties_described": "false",
            "title_level": "mid", "collected_reposts": "3", "collected_snapshots": "41",
        },
    )  # fmt: skip
    assert resp.status_code == 200, resp.text
    assert captured["facts"] == PostingFacts(
        branch="cloud",
        years_min=3,
        salary=PostingSalary(min=1000, max=1500, currency="usd", period="month"),
        salary_non_numeric=False,
        company_named=True,
        contacts=(ContactChannel.COMPANY_EMAIL, ContactChannel.ZALO),
        fees=2,
        duties_described=False,
        title_level="mid",
        collected_reposts=3,
        collected_snapshots=41,
    )
    assert (captured["role"], captured["level"], tuple(captured["have"]), tuple(captured["skills"])) == (
        "devops", "entry", ("docker",), ("docker", "aws"),
    )  # fmt: skip
    spy_client.get(URL, params={"role": "devops", "level": "entry", "salary_non_numeric": "true"})
    assert captured["facts"].salary_non_numeric is True and captured["facts"].salary is None


def test_ad22_su_kien_chua_doi_ket_qua_o_230(client: TestClient) -> None:
    plain_resp = _get(client, have=csv(HAVE_16_OF_18))
    facts_resp = _get(
        client,
        have=csv(HAVE_16_OF_18),
        years_min="3",
        company_named="false",
        fees="1",
        duties_described="false",
        title_level="senior",
        collected_reposts="2",
        collected_snapshots="30",
    )
    assert plain_resp.status_code == 200 and facts_resp.status_code == 200
    assert plain_resp.json() == facts_resp.json()  # #125 và #126 mới đọc chúng; `market` và `warnings` còn `not_ready`


@pytest.mark.parametrize("name", ["text", "jd", "q", "unrecognised", "quote", "fee_mentions", "role "])
def test_ad22_tham_so_la_bi_tu_choi_ke_ca_chu_tu_do(client: TestClient, name: str) -> None:
    resp = _get(client, **{name: SENTINEL})
    _invalid(resp)


def test_ad22_ky_nang_phai_nam_trong_bo_tu_vung(client: TestClient) -> None:
    # Cụm chưa nhận diện (ví dụ `Quarkus`) viết lại thành snake_case vẫn không qua được.
    _invalid(_get(client, skills="java,quarkus_framework_khong_co"))
    _invalid(_get(client, skills="Quarkus"))
    _invalid(_get(client, skills="java, sql"))
    _invalid(_get(client, skills="Tuyển Backend Developer"))
    _invalid(_get(client, skills="java,,sql"))
    _invalid(_get(client, skills=SENTINEL))


def test_ad22_moi_cum_chua_nhan_dien_cua_buoc_1_bi_tu_choi_o_buoc_2(client: TestClient) -> None:
    unrecognised = client.post("/api/v1/posting-reads", json={"text": BACKEND_TEXT}).json()["data"]["unrecognised"]
    assert unrecognised
    for phrase in unrecognised:
        slug = re.sub(r"[^a-z0-9]+", "_", phrase.casefold()).strip("_") or "x"
        _invalid(_get(client, skills=slug))
        _invalid(_get(client, skills=phrase))


def test_ad22_ma_cua_buoc_1_di_qua_buoc_2(client: TestClient) -> None:
    codes = [s["code"] for s in client.post("/api/v1/posting-reads", json={"text": BACKEND_TEXT}).json()["data"]["skills"]]
    assert codes == POSTING_SKILLS
    assert _get(client, skills=csv(codes)).status_code == 200


def test_ad22_ky_nang_toi_da_200_ma_dem_truoc_khi_loai_trung(client: TestClient) -> None:
    assert _get(client, skills=csv(["java"] * MAX_PROFILE_SKILLS)).status_code == 200
    _invalid(_get(client, skills=csv(["java"] * (MAX_PROFILE_SKILLS + 1))))


def test_ad22_ky_nang_trung_chi_tinh_mot_lan(client: TestClient) -> None:
    body = _get(client, skills="java,java,sql").json()
    assert [s["skill"]["code"] for s in body["data"]["match"]["skills"]] == ["java", "sql"]


def test_ad22_have_dung_chung_bo_doc_va_tran_voi_skill_rates(client: TestClient) -> None:
    assert _get(client, have=csv(["java"] * MAX_PROFILE_SKILLS)).status_code == 200
    _invalid(_get(client, have=csv(["java"] * (MAX_PROFILE_SKILLS + 1))))
    _invalid(_get(client, have="Java"))
    _invalid(_get(client, have="java,,sql"))
    deduped = _get(client, have="java,java,sql").json()
    assert deduped["data"]["match"]["level"]["points"] == 6  # java 3 + sql 3


def test_ad22_have_khong_kiem_voi_bo_tu_vung_ma_la_ky_nang_la_bi_bo_qua_nhu_skill_rates(client: TestClient) -> None:
    """`have` chỉ kiểm định dạng mã (như `skill-rates`); mã không có trong bộ từ vựng không khớp kỹ năng nào của tin nên không đổi kết quả."""
    plain = _get(client, have="java").json()
    with_unknown = _get(client, have="java,ky_nang_chua_tung_co").json()
    assert plain == with_unknown
    assert with_unknown["data"]["has_profile"] is True
    only_unknown = _get(client, have="ky_nang_chua_tung_co").json()["data"]
    assert only_unknown["has_profile"] is True  # có hồ sơ, nhưng không kỹ năng nào của tin có trong đó
    assert only_unknown["match"]["level"]["points"] == 0 and only_unknown["match"]["cv_first"] == []
    rates = client.get("/api/v1/skill-rates", params={"role": "backend", "level": "junior", "have": "ky_nang_chua_tung_co"})
    assert rates.status_code == 200 and not any(r["have"] for r in rates.json()["data"]["rows"])  # cùng quy tắc ở skill-rates


def test_ad22_ho_so_rong_la_khong_co_ho_so(client: TestClient) -> None:
    assert _get(client, have="").json()["data"]["has_profile"] is False


@pytest.mark.parametrize(
    "bad",
    [
        {"years_min": "-1"},
        {"years_min": "61"},
        {"years_min": "ba"},
        {"fees": "6"},
        {"fees": "-1"},
        {"company_named": "maybe"},
        {"contacts": "zalo,hello"},
        {"contacts": "zalo,zalo"},
        {"contacts": "Zalo"},
        {"salary_currency": "eur", "salary_period": "month", "salary_min": "1"},
        {"salary_currency": "vnd", "salary_period": "week", "salary_min": "1"},
        {"salary_min": "5"},  # thiếu tiền tệ và kỳ
        {"salary_currency": "vnd", "salary_period": "month"},  # có tiền tệ mà không có số
        {"salary_min": "20", "salary_max": "10", "salary_currency": "vnd", "salary_period": "month"},
        {"salary_min": "-5", "salary_currency": "vnd", "salary_period": "month"},
        {"salary_min": "1e3", "salary_currency": "vnd", "salary_period": "month"},
        {"salary_max": str(MAX_SALARY + 1), "salary_currency": "vnd", "salary_period": "month"},  # cùng trần với bước một
        {"duties_described": "maybe"},
        {"title_level": "ceo"},
        {"title_level": "unknown"},  # chức danh không cho biết cấp thì không gửi
        {"title_level": "Junior"},
        {"salary_non_numeric": "maybe"},
        {"salary_non_numeric": "true", "salary_min": "5", "salary_currency": "vnd", "salary_period": "month"},  # loại trừ nhau
        {"branch": "khong_co"},
        {"branch": "cloud"},  # nhánh của devops, role mặc định là backend
        {"branch": "Cloud"},
        {"collected_reposts": "1"},  # phải đi cặp
        {"collected_snapshots": "1"},
        {"collected_reposts": "-1", "collected_snapshots": "1"},
        {"collected_reposts": "1", "collected_snapshots": "-1"},
        {"collected_reposts": "100001", "collected_snapshots": "1"},
        {"collected_reposts": "1", "collected_snapshots": "10001"},
        {"collected_reposts": "x", "collected_snapshots": "1"},
    ],
)
def test_ad22_su_kien_sai_dinh_dang_la_422(client: TestClient, bad: dict[str, str]) -> None:
    _invalid(_get(client, **bad))


def test_ad22_role_va_level_bat_buoc_va_la_ma(client: TestClient) -> None:
    for missing in ("role", "level"):
        params = {k: v for k, v in BASE.items() if k != missing}
        _invalid(client.get(URL, params=params))
    _invalid(_get(client, level="ceo"))
    _invalid(_get(client, role="Backend Dev"))


def test_ad22_mo_ta_openapi_noi_ro_chi_ma_va_so() -> None:
    op = app.openapi()["paths"][URL]["get"]
    names = {p["name"] for p in op["parameters"]}
    assert names == {
        "role", "level", "branch", "have", "skills", "years_min", "salary_min", "salary_max", "salary_currency",
        "salary_period", "salary_non_numeric", "company_named", "contacts", "fees", "duties_described", "title_level",
        "collected_reposts", "collected_snapshots",
    }  # fmt: skip
    assert not names & {"text", "quote", "contact_quotes", "unrecognised", "fee_mentions", "url", "site"}  # chữ không đi lên


def test_ad22_tran_luong_cua_buoc_1_bang_tran_cua_buoc_2() -> None:
    """Một tin hợp lệ ở bước một không bao giờ bị 422 ở bước hai vì số lương quá trần."""
    assert market.MAX_SALARY == MAX_SALARY
    top = PostingSalary(min=MAX_SALARY, max=MAX_SALARY, currency="vnd", period="month")
    assert top.max == MAX_SALARY
    with pytest.raises(ValueError):
        PostingSalary(min=0, max=MAX_SALARY + 1, currency="vnd", period="month")
    ok = TestClient(app).get(
        URL,
        params={**BASE, "salary_min": str(MAX_SALARY), "salary_max": str(MAX_SALARY), "salary_currency": "usd", "salary_period": "year"},
    )
    assert ok.status_code == 200, ok.text


@pytest.mark.parametrize("text", [BACKEND_TEXT, FEE_TEXT, CLOUD_TEXT], ids=["backend", "fee", "cloud"])
def test_ad22_moi_tin_doc_duoc_o_buoc_1_deu_qua_buoc_2_tra_200(client: TestClient, text: str) -> None:
    """Chuỗi hai bước: POST đọc tin giả, dựng query từ kết quả (chỉ mã và số, như web), GET trả 200 cho mọi tin `is_posting`.

    Tin có phí có `level = unknown` (không ghi cấp): bước hai quay về ô mọi cấp thay vì 404.
    """
    read = client.post("/api/v1/posting-reads", json={"text": text}).json()["data"]
    assert read["is_posting"] is True
    query = query_from_read(read, have=["java", "sql", "docker"])
    resp = client.get(URL, params=query)
    assert resp.status_code == 200, (query, resp.text)
    data = resp.json()["data"]
    assert (data["role"], data["level"], data["branch"]) == (read["role"], read["level"], read["branch"])
    assert {s["skill"]["code"] for s in data["match"]["skills"]} == {s["code"] for s in read["skills"]}
    sent = resp.request.url.query.decode()
    assert SENTINEL not in resp.text and SENTINEL not in sent
    for phrase in (*read["unrecognised"], *read["fee_mentions"], *(q["quote"] for q in read["contact_quotes"])):
        assert phrase not in sent  # chữ nguyên văn không bao giờ lên máy chủ ở bước hai


def test_fr27_cap_khong_ghi_tin_quay_ve_o_moi_cap(client: TestClient) -> None:
    body = client.get(URL, params={**BASE, "level": "unknown"}).json()
    data = body["data"]
    assert data["level"] == "unknown" and data["cell_id"] == "vn.backend"
    assert body["meta"]["cells"]["vn.backend"]["fallback_label"]
    assert data["match"]["status"] == "ready"


def test_fr27_nhanh_la_ma_cua_vai_tro_va_duoc_lap_lai_o_response(client: TestClient) -> None:
    body = client.get(URL, params={"role": "devops", "level": "entry", "branch": "cloud", "skills": "docker,aws"}).json()
    assert body["data"]["branch"] == "cloud"
    assert _get(client).json()["data"]["branch"] is None
