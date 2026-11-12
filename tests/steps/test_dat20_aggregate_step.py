"""#93 — bước `aggregate`: ghi `stat_cells` và `stat_city_shares` của snapshot S."""

from dataclasses import replace
from datetime import date, timedelta

import pytest

from haido_core.steps.common import SnapshotClosedError, StepError
from tests.steps.conftest import Env, S

SD = date.fromisoformat(S)
# #285: nơi luôn có hàng (always_cities); tỉnh khác chỉ có hàng khi có tin.
CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "remote", "abroad", "unknown"]


def _day(back: int) -> str:
    return (SD - timedelta(days=back)).isoformat()


def _post(scraper_db, url: str, source: str = "itviec", **cols: str | None) -> None:
    scraper_db.job(url, source, **cols)


def _run(env: Env, scraper_db, urls_by_source: dict[str, list[str]], day: str = S, *, complete: bool = True) -> None:
    for source, urls in urls_by_source.items():
        scraper_db.day(source, day, urls, complete=complete)
    env.ingest(day)


def _shares(env: Env, role: str, day: str = S) -> dict[str, float]:
    rows = env.query(
        "SELECT city, share FROM haido.stat_city_shares "
        "WHERE snapshot_id = :d AND role = :r AND seniority = 'all' AND years = 'any'",  # #163, #280: test riêng
        d=day,
        r=role,
    )
    return dict(rows)


def _n(env: Env, role: str, scope: str, day: str = S) -> int:
    [(n,)] = env.query(
        "SELECT n FROM haido.stat_cells "
        "WHERE snapshot_id = :d AND role = :r AND scope = :s AND seniority = 'all' AND years = 'any'",
        d=day,
        r=role,
        s=scope,
    )
    return n


def _build(env: Env, scraper_db, jobs: dict[str, dict], source: str = "itviec") -> None:
    """Ghi `jobs` của scraper, thấy ở S, rồi chạy ingest, lifecycle, aggregate."""
    for url, cols in jobs.items():
        _post(scraper_db, url, source, **cols)
    _run(env, scraper_db, {source: list(jobs)})
    env.lifecycle()
    env.aggregate()


def test_dat20_moi_vai_tro_va_all_co_nam_dong_thanh_pho_ke_ca_khi_khong_co_tin(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)  # có lượt chạy nhưng không có tin nào
    env.ingest()
    env.lifecycle()
    result = env.aggregate()
    roles = ["all", *env.rules.roles]
    levels = 1 + len(env.rules.level_options)  # #163: cấp `all` cộng từng cấp lọc được
    levels *= 1 + len(env.rules.years_options)  # #280: `any` cộng từng mốc số năm
    always = len(env.rules.always_cities)
    assert (result.cells, result.shares) == (len(roles) * levels * (always + 1), len(roles) * levels * always)
    for role in roles:
        shares = _shares(env, role)
        assert set(shares) == set(CITIES)
        assert sum(shares.values()) == pytest.approx(1.0)
        assert _n(env, role, "vn") == 0
        assert _n(env, role, "da_nang") == 0  # Đà Nẵng luôn có hàng, kể cả n = 0
    assert env.count("stat_cells") == len(roles) * levels * (always + 1)
    assert env.count("stat_city_shares") == len(roles) * levels * always


def test_dat20_ty_trong_thanh_pho_va_n_dung_cho_tung_vai_tro(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            "b1": {"title": "Backend Developer", "location": "Hà Nội"},
            "b2": {"title": "Java Developer", "location": "Hà Nội, Việt Nam"},
            "b3": {"title": "Golang Developer", "location": "Đà Nẵng"},
            "b4": {"title": "Spring Boot Dev", "location": None},
            "q1": {"title": "QA Tester", "location": "Hồ Chí Minh"},
            "f1": {"title": "Frontend Dev", "location": "Hải Phòng"},
        },
    )
    assert _n(env, "backend", "vn") == 4
    zero = {"remote": 0.0, "abroad": 0.0}
    assert _shares(env, "backend") == {"ha_noi": 0.5, "ho_chi_minh": 0.0, "da_nang": 0.25, **zero, "unknown": 0.25}
    assert _shares(env, "qa") == {"ha_noi": 0.0, "ho_chi_minh": 1.0, "da_nang": 0.0, **zero, "unknown": 0.0}
    assert _n(env, "all", "vn") == 6
    assert _shares(env, "all")["hai_phong"] == pytest.approx(1 / 6)  # #285: Hải Phòng có hàng riêng
    assert "hai_phong" not in _shares(env, "backend")  # không có tin backend ở Hải Phòng thì không có hàng
    # mẫu nhỏ vẫn có số: Đà Nẵng n = 1 < 30
    assert _n(env, "backend", "da_nang") == 1
    for role in ("all", *env.rules.roles):
        assert sum(_shares(env, role).values()) == pytest.approx(1.0)


def test_dat20_nguon_chi_it_thi_tin_khong_ro_vai_tro_la_other_va_tin_ngoai_it_bi_loai(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            "it1": {"title": "Backend Developer", "location": "Hà Nội"},
            # itviec: nguồn chỉ-IT nên chức danh không rõ vai trò là Other. (#283: "Nhân viên kinh doanh" nay là
            # không thuộc IT vì có cụm "kinh doanh", nên ví dụ đổi sang chức danh không mang cụm nào.)
            "it2": {"title": "Chuyên viên sản phẩm", "location": "Hà Nội"},
            "kt": {"title": "Kế toán trưởng", "location": "Hà Nội"},  # luật loại tin không thuộc IT
        },
        source="itviec",
    )
    assert _n(env, "all", "vn") == 2
    assert _n(env, "other", "vn") == 1


def test_dat20_tin_ngoai_it_o_nguon_chung_bi_loai(env: Env, scraper_db) -> None:
    for url, title in (("a", "Backend Developer"), ("b", "Kế toán trưởng"), ("c", "Chuyên viên hành chính")):
        _post(scraper_db, url, "vietnamworks", title=title, location="Hà Nội")
    _run(env, scraper_db, {"vietnamworks": ["a", "b", "c"]})
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1
    assert _n(env, "backend", "vn") == 1


def test_dat20_cua_so_60_ngay_s_tru_59_trong_s_tru_60_ngoai(env: Env, scraper_db) -> None:
    for back, url in ((59, "in59"), (60, "out60"), (61, "out61")):
        _post(scraper_db, url, title="Backend Dev", location="Hà Nội")
        _run(env, scraper_db, {"itviec": [url]}, _day(back))
    _post(scraper_db, "today", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["today"]})
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 2  # in59 và today
    in_window = env.query("SELECT count(*) FROM haido.stat_job_lifecycle WHERE snapshot_id = :d AND in_window", d=S)
    assert in_window == [(3,)]  # cột in_window cho 0 đến 60 ngày (61 ngày), không dùng cho phép đếm


def test_dat20_tin_chi_thay_o_luot_chay_loi_khong_co_dong_vong_doi_thi_khong_dem(env: Env, scraper_db) -> None:
    _post(scraper_db, "ok", title="Backend Dev", location="Hà Nội")
    _post(scraper_db, "bad", title="Backend Dev", location="Hà Nội")
    scraper_db.day("itviec", S, ["ok"])
    scraper_db.day("zalo", S, ["bad"], complete=False)
    env.ingest()
    env.lifecycle()
    assert env.query("SELECT count(*) FROM haido.stat_job_lifecycle") == [(1,)]
    env.aggregate()
    assert _n(env, "all", "vn") == 1


def test_dat20_moi_tin_dem_mot_lan_du_thay_nhieu_ngay(env: Env, scraper_db) -> None:
    _post(scraper_db, "x", title="Backend Dev", location="Hà Nội")
    for back in (2, 1, 0):
        _run(env, scraper_db, {"itviec": ["x"]}, _day(back))
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1


def test_dat20_dung_du_kien_tai_s_khong_dung_phien_ban_moi_hon(env: Env, scraper_db) -> None:
    _post(scraper_db, "x", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["x"]})
    _post(scraper_db, "x", title="QA Tester", location="Đà Nẵng")  # scraper ghi đè ở ngày sau
    _run(env, scraper_db, {"itviec": ["x"]}, _day(-1))
    env.lifecycle()
    env.aggregate()
    assert _n(env, "backend", "ha_noi") == 1
    assert _n(env, "qa", "vn") == 0


def test_dat20_dau_vao_phan_loai_cap_bac_ghep_job_level_va_experience_level(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            "a": {"title": "Backend Dev", "job_level": "Senior", "experience_level": "5 năm"},
            "b": {"title": "Backend Dev", "job_level": None, "experience_level": "Fresher"},
            "c": {"title": "Junior Java Developer", "job_level": None, "experience_level": None},
            "d": {"title": "Backend Dev", "job_level": "Nhân viên", "experience_level": "Intern"},
            "e": {"title": "Backend Dev"},
        },
    )
    [(mix,)] = env.query("SELECT seniority_mix FROM haido.stat_cells WHERE role = 'all' AND scope = 'vn' AND seniority = 'all' AND years = 'any'")
    assert mix == {"senior": 1, "fresher": 1, "junior": 1, "intern": 1, "unknown": 1}


def test_dat20_moi_o_luu_n_pha_cap_bac_va_config_version(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            "a": {"title": "Backend Dev", "location": "Hà Nội", "job_level": "Junior"},
            "b": {"title": "Backend Dev", "location": "Hà Nội", "job_level": "Junior"},
            "c": {"title": "Backend Dev", "location": "Đà Nẵng", "job_level": "Senior"},
        },
    )
    rows = env.query(
        "SELECT scope, n, seniority_mix, branch, seniority, config_version FROM haido.stat_cells "
        "WHERE role = 'backend' AND seniority = 'all' AND years = 'any' ORDER BY scope"
    )
    by_scope = {r[0]: r for r in rows}
    assert by_scope["vn"][1:3] == (3, {"junior": 2, "senior": 1})
    assert by_scope["ha_noi"][1:3] == (2, {"junior": 2})
    assert by_scope["da_nang"][1:3] == (1, {"senior": 1})
    assert by_scope["remote"][1:3] == (0, {})  # #285: nơi luôn có hàng, kể cả n = 0
    assert {(r[3], r[4], r[5]) for r in rows} == {("all", "all", env.rules.config_version)}


def test_dat20_chay_lai_khi_s_van_open_ghi_de_khong_nhan_doi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    before = env.count("stat_cells"), env.count("stat_city_shares")
    _post(scraper_db, "b", title="QA Tester", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a", "b"]})  # ingest lại cho S
    env.lifecycle()  # phải chạy lại lifecycle trước aggregate
    env.aggregate()
    assert (env.count("stat_cells"), env.count("stat_city_shares")) == before
    assert _n(env, "all", "vn") == 2
    assert _n(env, "qa", "vn") == 1


@pytest.mark.determinism
def test_dat20_determinism_hai_lan_aggregate_ra_cung_hang(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            f"u{i}": {
                "title": ("Backend Dev", "QA Tester", "Mobile Android", "DevOps Engineer")[i % 4],
                "location": ("Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", None)[i % 5],
                "job_level": ("Junior", "Senior", None)[i % 3],
            }
            for i in range(37)
        },
    )
    cells = "SELECT * FROM haido.stat_cells ORDER BY snapshot_id, role, branch, seniority, years, scope"
    shares = "SELECT * FROM haido.stat_city_shares ORDER BY snapshot_id, role, seniority, years, city"
    first = env.query(cells), env.query(shares)
    env.aggregate()
    assert (env.query(cells), env.query(shares)) == first
    # 18 vai trò (#284) × 9 cấp lọc × 6 mã số năm (#280); mỗi bộ lọc ít nhất 6 nơi luôn có + vn (#285), cộng Cần Thơ
    # khi bộ lọc có tin ở đó.
    assert len(first[0]) >= 18 * 7 * 9 * 6 and len(first[1]) >= 18 * 6 * 9 * 6
    assert any("can_tho" in row for row in first[1])


@pytest.mark.parametrize("status", ["published", "partial"])
def test_dat20_snapshot_da_chot_thi_tu_choi_va_khong_ghi(env: Env, scraper_db, status: str) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    snapshot = "SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope"
    before = env.query(snapshot)
    with env.write.begin() as conn:
        conn.exec_driver_sql(f"UPDATE haido.snapshots SET status = '{status}'")
    with pytest.raises(SnapshotClosedError, match="đã chốt"):
        env.aggregate(rules=replace(env.rules, config_version="moi"))
    assert env.query(snapshot) == before


def test_dat20_snapshot_da_chot_va_chua_tung_aggregate_thi_van_khong_ghi_hang_nao(env: Env, scraper_db) -> None:
    _run(env, scraper_db, {"itviec": []})
    env.lifecycle()
    with env.write.begin() as conn:
        conn.exec_driver_sql("UPDATE haido.snapshots SET status = 'published'")
    with pytest.raises(SnapshotClosedError):
        env.aggregate()
    assert env.count("stat_cells") == env.count("stat_city_shares") == 0


def test_dat20_snapshot_chua_mo_thi_bao_loi(env: Env) -> None:
    with pytest.raises(StepError, match="chưa mở"):
        env.aggregate()
    assert env.count("stat_cells") == 0


def test_dat20_ngay_sai_thi_khong_ghi(env: Env) -> None:
    with pytest.raises(StepError, match="YYYY-MM-DD"):
        env.aggregate("2026-13-01")


def test_dat20_nhan_chua_co_trong_bang_thi_buoc_loi_va_khong_ghi_gi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    before = env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope")
    _post(scraper_db, "b", title="QA Tester", location="Đà Nẵng")
    _run(env, scraper_db, {"itviec": ["a", "b"]})
    env.lifecycle()
    broken = {k: v for k, v in env.rules.city_codes.items() if k != "Đà Nẵng"}
    with pytest.raises(StepError, match="Đà Nẵng"):
        env.aggregate(rules=replace(env.rules, city_codes=broken))
    assert env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope") == before


def test_dat20_nhan_vai_tro_la_cung_khong_duoc_doan(env: Env, scraper_db) -> None:
    _post(scraper_db, "a", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a"]})
    env.lifecycle()
    broken = {k: v for k, v in env.rules.role_codes.items() if k != "Backend"}
    with pytest.raises(StepError, match="Backend"):
        env.aggregate(rules=replace(env.rules, role_codes=broken))
    assert env.count("stat_cells") == 0


def test_dat20_loi_giua_chung_thi_giu_nguyen_hang_cu(env: Env, scraper_db, monkeypatch: pytest.MonkeyPatch) -> None:
    from haido_core.db import snapshot_store

    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    before = env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope")
    real = snapshot_store.replace_stats

    def after_write(*args, **kwargs):
        real(*args, **kwargs)
        raise RuntimeError("giả lập lỗi sau khi ghi")

    monkeypatch.setattr(snapshot_store, "replace_stats", after_write)
    with pytest.raises(RuntimeError):
        env.aggregate(rules=replace(env.rules, config_version="moi"))
    assert env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope") == before


def test_dat20_chua_chay_lifecycle_thi_tu_choi_va_khong_ghi_hang_nao(env: Env, scraper_db) -> None:
    _post(scraper_db, "a", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a"]})
    with pytest.raises(StepError, match="lifecycle"):
        env.aggregate()
    assert env.count("stat_cells") == 0
    assert env.count("stat_city_shares") == 0


def test_dat20_ingest_chay_lai_them_tin_ma_chua_chay_lai_lifecycle_thi_tu_choi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    before = env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope")
    _post(scraper_db, "b", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a", "b"]})
    with pytest.raises(StepError, match="lifecycle"):
        env.aggregate()
    assert env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope") == before
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 2


def test_dat20_loi_value_error_cua_tong_hop_thanh_step_error_tieng_viet(
    env: Env, scraper_db, monkeypatch: pytest.MonkeyPatch
) -> None:
    from haido_core.steps import aggregate as step

    _post(scraper_db, "a", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a"]})
    env.lifecycle()

    def broken(*args, **kwargs):
        raise ValueError("không cộng lại bằng toàn quốc")

    monkeypatch.setattr(step, "aggregate_city_shares", broken)
    with pytest.raises(StepError, match="Không tổng hợp được"):
        env.aggregate()
    assert env.count("stat_cells") == 0


# ---------------------------------------------------------------- #259: nguồn có tin được đếm trong cửa sổ 60 ngày


def _sources(env: Env, day: str = S) -> list[str]:
    return [r[0] for r in env.query("SELECT source FROM haido.stat_sources WHERE snapshot_id = :d ORDER BY source", d=day)]


def test_dat259_nguon_chay_tay_muoi_ngay_truoc_van_duoc_liet_ke_du_khong_chay_o_s(env: Env, scraper_db) -> None:
    _post(scraper_db, "tc", "topcv", title="Backend Dev", location="Hà Nội")
    _post(scraper_db, "iv", "itviec", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"topcv": ["tc"]}, _day(10))  # chạy tay, không chạy ở S
    _run(env, scraper_db, {"itviec": ["iv"]})
    env.lifecycle()
    env.aggregate()
    assert env.query("SELECT 1 FROM haido.pipeline_runs WHERE snapshot_id = :d AND source = 'topcv'", d=S) == []
    assert _sources(env) == ["itviec", "topcv"]


def test_dat259_nguon_chay_o_s_nhung_khong_co_tin_nao_duoc_dem_thi_khong_liet_ke(env: Env, scraper_db) -> None:
    _post(scraper_db, "iv", "itviec", title="Backend Dev", location="Hà Nội")
    _post(scraper_db, "old", "momo", title="Backend Dev", location="Hà Nội")
    _post(scraper_db, "kt", "vietnamworks", title="Kế toán trưởng", location="Hà Nội")  # không thuộc IT: không đếm
    _run(env, scraper_db, {"momo": ["old"]}, _day(60))  # last_seen ngoài cửa sổ 60 ngày
    _run(
        env,
        scraper_db,
        {"itviec": ["iv"], "momo": [], "zalo": [], "vietnamworks": ["kt"]},
    )
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1
    assert _sources(env) == ["itviec"]  # momo, zalo, vietnamworks chạy ở S nhưng không có tin nào được đếm


def test_dat259_bien_cua_so_59_ngay_trong_60_ngay_ngoai(env: Env, scraper_db) -> None:
    _post(scraper_db, "a", "topcv", title="Backend Dev", location="Hà Nội")
    _post(scraper_db, "b", "momo", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"topcv": ["a"]}, _day(59))
    _run(env, scraper_db, {"momo": ["b"]}, _day(60))
    _run(env, scraper_db, {"itviec": []})
    env.lifecycle()
    env.aggregate()
    assert _sources(env) == ["topcv"]


def test_dat259_danh_sach_a_z_khong_phu_thuoc_thu_tu_va_n_bang_do_dai(env: Env, scraper_db) -> None:
    for source in ("zalo", "topdev", "momo", "itviec"):
        _post(scraper_db, f"u-{source}", source, title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {s: [f"u-{s}"] for s in ("zalo", "topdev", "momo", "itviec")})
    env.lifecycle()
    env.aggregate()
    assert _sources(env) == ["itviec", "momo", "topdev", "zalo"]


def test_dat259_chay_lai_aggregate_ghi_de_danh_sach_nguon_khong_nhan_doi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    assert _sources(env) == ["itviec"]
    _post(scraper_db, "z", "zalo", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"zalo": ["z"]})
    env.lifecycle()
    env.aggregate()
    env.aggregate()
    assert _sources(env) == ["itviec", "zalo"]


def test_dat259_nguon_ghi_cung_transaction_voi_so_lieu_loi_giua_chung_thi_giu_danh_sach_cu(
    env: Env, scraper_db, monkeypatch: pytest.MonkeyPatch
) -> None:
    _build(env, scraper_db, {"a": {"title": "Backend Dev", "location": "Hà Nội"}})
    cells_before = env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope")
    shares_before = env.query("SELECT * FROM haido.stat_city_shares ORDER BY role, seniority, years, city")
    _post(scraper_db, "z", "zalo", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"zalo": ["z"]})
    env.lifecycle()
    from haido_core.db import snapshot_store

    real = snapshot_store.replace_stats

    def after_write(*args, **kwargs):
        real(*args, **kwargs)
        raise RuntimeError("giả lập lỗi sau khi ghi")

    monkeypatch.setattr(snapshot_store, "replace_stats", after_write)
    with pytest.raises(RuntimeError):
        env.aggregate()
    assert _sources(env) == ["itviec"]
    assert env.query("SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope") == cells_before
    assert env.query("SELECT * FROM haido.stat_city_shares ORDER BY role, seniority, years, city") == shares_before


def test_dat259_ghi_de_nguon_cua_s2_khong_dong_den_nguon_cua_snapshot_s1_da_chot(env: Env, scraper_db) -> None:
    s1 = _day(1)
    _post(scraper_db, "a", "itviec", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"itviec": ["a"]}, s1)
    env.lifecycle(s1)
    env.aggregate(s1)
    env.publish(s1)
    assert _sources(env, s1) == ["itviec"]
    _post(scraper_db, "z", "zalo", title="Backend Dev", location="Hà Nội")
    _run(env, scraper_db, {"zalo": ["z"]})
    env.lifecycle()
    env.aggregate()
    assert "zalo" in _sources(env)
    assert _sources(env, s1) == ["itviec"]


def test_dat259_snapshot_khong_co_tin_nao_thi_khong_co_nguon_nao(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)
    env.ingest()
    env.lifecycle()
    env.aggregate()
    assert _sources(env) == []


# ---------------------------------------------------------------- #263: tin LinkedIn không vào số công khai


def test_dat263_tin_linkedin_khong_vao_stat_cells_stat_city_shares_va_danh_sach_nguon(env: Env, scraper_db) -> None:
    _post(scraper_db, "li", "linkedin", title="Backend Developer", location="Hà Nội")
    _post(scraper_db, "li2", "linkedin", title="QA Tester", location="Hồ Chí Minh")
    _post(scraper_db, "iv", "itviec", title="Backend Developer", location="Đà Nẵng")
    _run(env, scraper_db, {"linkedin": ["li", "li2"]}, _day(5))
    _run(env, scraper_db, {"itviec": ["iv"]})
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1
    assert _n(env, "backend", "ha_noi") == 0
    assert _n(env, "qa", "vn") == 0
    assert _shares(env, "backend")["da_nang"] == 1.0
    assert _sources(env) == ["itviec"]
    # không hàng stat_* nào đếm tin LinkedIn: tổng n các thành phố của mọi vai trò chỉ là tin của itviec
    [(total,)] = env.query("SELECT sum(n) FROM haido.stat_cells WHERE scope <> 'vn' AND role = 'all' AND seniority = 'all' AND years = 'any'")
    assert total == 1


def test_dat263_snapshot_chi_co_linkedin_thi_so_bang_0_va_khong_co_nguon(env: Env, scraper_db) -> None:
    _post(scraper_db, "li", "linkedin", title="Backend Developer", location="Hà Nội")
    _run(env, scraper_db, {"linkedin": ["li"]})
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 0
    assert _sources(env) == []


def test_dat263_nguon_bi_loai_lay_tu_config_khong_viet_cung_trong_ma(env: Env, scraper_db) -> None:
    _post(scraper_db, "li", "linkedin", title="Backend Developer", location="Hà Nội")
    _post(scraper_db, "iv", "itviec", title="Backend Developer", location="Hà Nội")
    _run(env, scraper_db, {"linkedin": ["li"], "itviec": ["iv"]})
    env.lifecycle()
    env.aggregate(rules=replace(env.rules, excluded_sources=("itviec",)))
    assert _n(env, "all", "vn") == 1
    assert _sources(env) == ["linkedin"]
    env.aggregate(rules=replace(env.rules, excluded_sources=()))
    assert _n(env, "all", "vn") == 2
    assert _sources(env) == ["itviec", "linkedin"]


def test_dat263_nguon_bi_loai_khong_phan_biet_hoa_thuong_o_du_lieu(env: Env, scraper_db) -> None:
    _post(scraper_db, "li", "LinkedIn", title="Backend Developer", location="Hà Nội")
    _post(scraper_db, "iv", "itviec", title="Backend Developer", location="Hà Nội")
    _run(env, scraper_db, {"LinkedIn": ["li"], "itviec": ["iv"]})
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1
    assert _sources(env) == ["itviec"]


def test_dat28_hai_nguon_cung_cong_ty_va_chuc_danh_dem_mot_va_lay_thanh_pho_dai_dien(env: Env, scraper_db) -> None:
    _post(scraper_db, "https://itviec.test/backend", "itviec", title="Backend Dev", company="FPT", location="Đà Nẵng")
    _post(
        scraper_db,
        "https://topcv.test/backend",
        "topcv",
        title="Backend Dev",
        company="Công ty TNHH FPT",
        location="Hà Nội",
        job_level="Senior",
    )
    _run(
        env,
        scraper_db,
        {"itviec": ["https://itviec.test/backend"], "topcv": ["https://topcv.test/backend"]},
    )
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "vn") == 1
    assert _n(env, "backend", "vn") == 1
    assert _n(env, "backend", "da_nang") == 1
    assert _n(env, "backend", "ha_noi") == 0
    assert _sources(env) == ["itviec", "topcv"]
