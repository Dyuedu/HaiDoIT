"""#230 — production không bao giờ phục vụ tin dán giả: `posting_check` đọc `stat`, `posting-reads` đọc nguồn `model`.

Quy tắc chung của #309 (mọi khóa `SOURCE_ENV` là `stat` ở prod) đã bao `posting_check`; test này thêm phần riêng của #230:
nguồn đọc chữ dán có biến riêng vì nó không phải số liệu thị trường, và cả hai nguồn của prod đều từ chối thay vì trả fixture.
"""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from haido_api.main import app, create_app
from haido_api.market_source import CheckUnavailable, UnknownCell
from haido_api.posting_read import (
    READER_ENV,
    FakePostingReader,
    ModelPostingReader,
    load_reader,
)
from haido_api.routes.market import SOURCE_ENV, load_sources
from haido_api.schemas.posting import PostingFacts
from haido_api.stat_market import StatMarket

ROOT = Path(__file__).resolve().parents[2]
TEXT = "Tuyển Backend Developer Java Spring Boot, 1 năm kinh nghiệm. " * 5  # dài hơn 200 ký tự, có dấu IT


def _api_env(compose: str) -> dict[str, str]:
    env = yaml.safe_load((ROOT / "deploy" / compose).read_text(encoding="utf-8"))["services"]["api"]["environment"]
    return {k: str(v) for k, v in env.items()}


def test_gh230_posting_check_la_mot_khoa_cua_source_env_va_prod_dat_stat() -> None:
    assert SOURCE_ENV["posting_check"] == "HAIDO_MARKET_SOURCE_POSTING_CHECK"
    assert _api_env("compose.prod.yml")[SOURCE_ENV["posting_check"]] == "stat"


def test_gh230_prod_dat_nguon_doc_chu_dan_la_model_khong_phai_gia() -> None:
    assert _api_env("compose.prod.yml")[READER_ENV] == "model"
    assert _api_env("compose.local.yml").get(READER_ENV, "fake") == "fake"  # smoke của CI dùng bản giả


def test_gh230_prod_dung_nguon_that_cho_ca_hai_buoc() -> None:
    env = _api_env("compose.prod.yml")
    assert isinstance(load_sources({k: v for k, v in env.items() if k in SOURCE_ENV.values()})["posting_check"], StatMarket)
    reader = load_reader(env)
    assert isinstance(reader, ModelPostingReader) and not isinstance(reader, FakePostingReader)


def test_gh230_prod_khong_tra_du_lieu_gia_o_ca_hai_buoc() -> None:
    env = _api_env("compose.prod.yml")
    app = create_app(
        load_sources({k: v for k, v in env.items() if k in SOURCE_ENV.values()}), posting_reader=load_reader(env)
    )
    client = TestClient(app, raise_server_exceptions=False)
    read = client.post("/api/v1/posting-reads", json={"text": TEXT})
    assert read.status_code == 503 and read.json()["error"]["code"] == "read_unavailable"
    check = client.get(
        "/api/v1/posting-check", params={"role": "backend", "level": "junior", "skills": "java,sql"}
    )
    # Chưa có số thật: "chưa sẵn sàng, thử lại sau" (503 `check_unavailable`), không phải 404 `unknown_cell`, vì 404 là "không có
    # số cho vai trò và cấp này" mà màn hiểu là kết quả cuối, không thử lại.
    assert check.status_code == 503, check.text
    assert check.json()["error"]["code"] == "check_unavailable"
    assert "data" not in check.json()


def test_gh230_prod_check_unavailable_khac_unknown_cell_cua_vai_tro_khong_co_so() -> None:
    env = _api_env("compose.prod.yml")
    sources = load_sources({k: v for k, v in env.items() if k in SOURCE_ENV.values()})
    with pytest.raises(CheckUnavailable):
        sources["posting_check"].posting_check(role="backend", level="junior", have=(), skills=("java",), facts=PostingFacts())
    assert not issubclass(CheckUnavailable, UnknownCell) and not issubclass(UnknownCell, CheckUnavailable)
    unknown = TestClient(app).get("/api/v1/posting-check", params={"role": "khong_ton_tai", "level": "junior"})
    assert (unknown.status_code, unknown.json()["error"]["code"]) == (404, "unknown_cell")


def test_gh230_check_unavailable_khai_503_trong_openapi_va_co_snapshot_date_null() -> None:
    op = app.openapi()["paths"]["/api/v1/posting-check"]["get"]
    assert op["responses"]["503"]["content"]["application/json"]["schema"]["$ref"].endswith("ErrorEnvelope")
    assert "check_unavailable" in op["responses"]["503"]["description"]
    prod = TestClient(create_app({name: StatMarket() for name in SOURCE_ENV}, posting_reader=ModelPostingReader()), raise_server_exceptions=False)
    body = prod.get("/api/v1/posting-check", params={"role": "backend", "level": "junior"}).json()
    assert body["error"]["snapshot_date"] is None and body["error"]["message"]


@pytest.mark.parametrize("compose", ["compose.demo.yml", "compose.loadtest.yml"])
def test_gh230_demo_va_loadtest_cung_la_model_va_stat_nhu_prod(compose: str) -> None:
    """Demo và loadtest không phục vụ tin dán giả: bản giả chọn kết quả từ vài chữ khóa, người xem demo sẽ tưởng là số thật.
    Nên cả hai đặt `HAIDO_POSTING_READER: model` (503 `read_unavailable` tới #232) và `posting_check: stat` (503 `check_unavailable` tới #234)."""
    env = _api_env(compose)
    assert env[READER_ENV] == "model"
    assert env[SOURCE_ENV["posting_check"]] == "stat"


def test_gh230_bien_nguon_doc_khong_dat_thi_mac_dinh_fake_nhu_cac_nguon_khac() -> None:
    """Fail closed là việc của compose prod (các test trên khóa `model`); mã giữ mặc định `fake` như `SOURCE_ENV` (#309)."""
    assert isinstance(load_reader({}), FakePostingReader)


@pytest.mark.parametrize("compose", ["compose.local.yml"])
def test_gh230_local_giu_nguon_gia(compose: str) -> None:
    assert _api_env(compose).get(SOURCE_ENV["posting_check"], "fake") == "fake"
