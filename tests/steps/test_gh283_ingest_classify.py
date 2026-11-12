"""#283 — `ingest` phân loại lúc văn bản JD còn trong bộ nhớ và chỉ lưu nhãn, mã; `aggregate` dùng nhãn đã lưu."""

import dataclasses
import json

from haido_core.config import load_classify_config
from haido_core.steps.aggregate import aggregate_snapshot
from haido_core.steps.ingest import ingest_snapshot
from tests.steps.conftest import Env, S

S2 = "2026-11-04"
DEVOPS_JD = (
    "Mô tả công việc\nVận hành hạ tầng.\n"
    "Yêu cầu\nPython, Docker, Kubernetes, Terraform, AWS, CI/CD, Linux, Prometheus. Python nâng cao.\n"
    "Quyền lợi\nHọc machine learning miễn phí.\n"
)


def _facts(env: Env) -> list:
    return env.query(
        "SELECT p.source_url, f.snapshot_id, f.role, f.branch, f.seniority, f.skills, f.years_min, f.classify_version "
        "FROM haido.job_posting_facts f JOIN haido.job_postings p ON p.id = f.posting_id "
        "ORDER BY p.source_url, f.snapshot_id"
    )


def test_gh283_ingest_luu_nhan_ma_ky_nang_co_so_luot_va_phien_ban(env: Env, scraper_db) -> None:
    scraper_db.job("u1", "topcv", title="Chuyên viên", location="Hà Nội", description=DEVOPS_JD,
                   years_experience_min=None)
    scraper_db.job("u2", "topcv", title="Business Analyst", location="Hà Nội",
                   description="Yêu cầu\nKhông yêu cầu kinh nghiệm.", years_experience_min=None)
    scraper_db.day("topcv", S, ["u1", "u2"])
    env.ingest()
    rows = {r[0]: r for r in _facts(env)}
    version = load_classify_config().version
    u1 = rows["u1"]
    assert u1[2] == "DevOps"
    skills = u1[5] if isinstance(u1[5], dict) else json.loads(u1[5])
    assert skills["python"] == 2
    assert skills["docker"] == 1
    assert "machine_learning" not in skills
    assert u1[7] == version
    u2 = rows["u2"]
    assert (u2[2], u2[3], u2[4], u2[6]) == ("BA/PO/PM", "Business Analyst", "Fresher", 0.0)


def test_gh283_ingest_chay_lai_khong_them_phien_ban_khi_nhan_da_dung(env: Env, scraper_db) -> None:
    scraper_db.job("u1", "topcv", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD)
    scraper_db.day("topcv", S, ["u1"])
    env.ingest()
    env.ingest()
    assert env.count("job_posting_facts") == 1


def test_gh283_lam_moi_tin_trong_cua_so_co_phien_ban_luat_cu(env: Env, scraper_db) -> None:
    current = load_classify_config()
    old = dataclasses.replace(current, version="classify-cu")
    scraper_db.job("u1", "topcv", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD)
    scraper_db.job("u2", "topcv", title="Data Analyst", location="Hà Nội")
    scraper_db.day("topcv", S, ["u1", "u2"])
    ingest_snapshot(S, reader=env.reader, engine=env.write, rules=env.rules, classify=old)
    # Ngày sau chỉ thấy u2; u1 vẫn trong cửa sổ nhưng nhãn là của luật cũ.
    scraper_db.day("topcv", S2, ["u2"])
    ingest_snapshot(S2, reader=env.reader, engine=env.write, rules=env.rules, classify=current)
    rows = _facts(env)
    by_url: dict[str, list] = {}
    for r in rows:
        by_url.setdefault(r[0], []).append(r)
    assert [(str(r[1]), r[7]) for r in by_url["u1"]] == [(S, "classify-cu"), (S2, current.version)]
    assert [(str(r[1]), r[7]) for r in by_url["u2"]] == [(S, "classify-cu"), (S2, current.version)]
    # Lượt sau cùng luật: không thêm gì.
    ingest_snapshot(S2, reader=env.reader, engine=env.write, rules=env.rules, classify=current)
    assert len(_facts(env)) == 4


def _n(env: Env, role: str) -> int:
    rows = env.query(
        "SELECT n FROM haido.stat_cells WHERE snapshot_id = :d AND role = :r AND seniority = 'all' "
        "AND years = 'any' AND scope = 'vn'",
        d=S,
        r=role,
    )
    return rows[0][0] if rows else 0


def test_gh283_aggregate_dung_nhan_da_luu(env: Env, scraper_db) -> None:
    scraper_db.job("u1", "topcv", title="Chuyên viên", location="Hà Nội", description=DEVOPS_JD)
    scraper_db.job("u2", "topcv", title="Data Scientist", location="Hà Nội")
    scraper_db.day("topcv", S, ["u1", "u2"])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    assert _n(env, "devops") == 1
    assert _n(env, "data_scientist") == 1  # #284: Data Scientist có mã riêng (trước đó báo cáo như AI/ML)


def test_gh283_aggregate_phan_loai_tu_truong_dong_khi_nhan_khong_cua_luat_hien_tai(env: Env, scraper_db) -> None:
    current = load_classify_config()
    other = dataclasses.replace(current, version="classify-khac")
    scraper_db.job("u1", "topcv", title="Chuyên viên", location="Hà Nội", description=DEVOPS_JD)
    scraper_db.day("topcv", S, ["u1"])
    env.ingest()
    env.lifecycle()
    aggregate_snapshot(S, engine=env.write, rules=env.rules, classify=other)
    # Không có văn bản: chức danh "Chuyên viên" ở topcv không đủ để là tin IT.
    assert _n(env, "devops") == 0
    assert _n(env, "all") == 0
