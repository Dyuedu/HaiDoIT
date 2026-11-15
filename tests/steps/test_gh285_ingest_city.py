"""#285 — ingest lưu nơi làm việc (kể cả từ dòng địa chỉ của JD); aggregate ghi hàng của tỉnh có tin."""

from tests.steps.conftest import Env, S


def _cities(env: Env) -> dict[str, str]:
    rows = env.query(
        "SELECT p.source_url, f.city FROM haido.job_posting_facts f JOIN haido.job_postings p ON p.id = f.posting_id"
    )
    return dict(rows)


def _build(env: Env, scraper_db) -> None:
    scraper_db.job("hn", "itviec", title="Backend Developer", location="Hà Nội")
    scraper_db.job("bd", "itviec", title="Backend Developer", location="Bình Dương")
    scraper_db.job("jd", "itviec", title="Backend Developer", location=None,
                   description="Yêu cầu\nJava.\nĐịa điểm làm việc: KCN Quế Võ, Bắc Ninh")
    scraper_db.job("rm", "itviec", title="Backend Developer", location=None,
                   description="Hình thức: Remote 100%, làm việc từ xa.")
    scraper_db.job("jp", "itviec", title="Backend Developer", location="Quốc tế")
    for source in env.rules.auto_sources:
        scraper_db.day(source, S, ["hn", "bd", "jd", "rm", "jp"] if source == "itviec" else [])
    env.ingest()


def test_gh285_ingest_luu_noi_lam_viec(env: Env, scraper_db) -> None:
    _build(env, scraper_db)
    assert _cities(env) == {"hn": "Hà Nội", "bd": "TP.HCM", "jd": "Bắc Ninh", "rm": "Remote", "jp": "Nước ngoài"}


def test_gh285_aggregate_ghi_hang_tinh_co_tin_va_khong_ghi_tinh_khong_co(env: Env, scraper_db) -> None:
    _build(env, scraper_db)
    env.lifecycle()
    env.aggregate()
    rows = dict(
        env.query(
            "SELECT city, share FROM haido.stat_city_shares WHERE snapshot_id = :d AND role = 'backend' "
            "AND seniority = 'all' AND years = 'any'",
            d=S,
        )
    )
    assert set(rows) == {"ha_noi", "ho_chi_minh", "da_nang", "bac_ninh", "remote", "abroad", "unknown"}
    assert rows["bac_ninh"] == 0.2
    assert rows["ho_chi_minh"] == 0.2
    assert rows["remote"] == 0.2
    assert rows["abroad"] == 0.2
    assert "other" not in rows
