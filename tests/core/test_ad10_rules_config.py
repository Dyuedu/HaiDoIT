"""AD-10 — ngưỡng và danh sách nguồn đọc từ config có phiên bản (Story 1.4, #93)."""

import ast
import re
from pathlib import Path

import pytest

from haido_core.config import ConfigError, load_rules

PDF = "application/pdf"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
AUTO = ("zalo", "itnavi", "careerlink", "vietnamworks", "momo", "topdev", "itviec")

NOTE = '[[coverage_notes]]\ncode = "n_sources"\ntext = "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên {n} nguồn."\n'
SOURCES = '[sources]\nauto = ["a", "b"]\nexcluded = ["x"]\npriority = ["a", "b"]\n'
CITY = (
    '[labels.city]\n"Hà Nội" = "ha_noi"\n"Hồ Chí Minh" = "ho_chi_minh"\n"Đà Nẵng" = "da_nang"\n'
    '"Khác" = "other"\n"không xác định" = "unknown"\n'
)
ROLE = '[labels.role]\n"Backend" = "backend"\n"Other" = "other"\n'
LEVEL = '[labels.level]\n"Junior" = "junior"\n"không xác định" = "unknown"\n'

CV = f'cv_max_bytes = 5242880\ncv_types = ["{PDF}", "{DOCX}"]\n'

BASE = (
    'config_version = "t"\nwindow_days = 60\nmin_sample = 30\ntheta_core = 0.3\ntheta_common = 0.1\n'
    f'roles = ["backend", "other"]\n{CV}\n'
    f"{SOURCES}\n{NOTE}\n{CITY}\n{ROLE}\n{LEVEL}"
)


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "rules.toml"
    path.write_text(body, encoding="utf-8")
    return path


def _base(tmp_path: Path, *, drop: str | None = None, **swap: str) -> Path:
    """File cấu hình đủ khóa; `drop` bỏ một dòng, `swap` đổi `khóa = giá trị` thành giá trị mới."""
    body = BASE
    for key, value in swap.items():
        body = re.sub(rf"^{key} = .*$", f"{key} = {value}", body, count=1, flags=re.MULTILINE)
    if drop is not None:
        body = re.sub(rf"^{drop} = .*\n", "", body, count=1, flags=re.MULTILINE)
    return _write(tmp_path, body)


def test_ad10_rules_mac_dinh_co_phien_ban_cua_so_va_bay_nguon() -> None:
    rules = load_rules()
    assert rules.config_version
    assert rules.window_days == 60
    assert rules.auto_sources == AUTO
    assert "topcv" not in rules.auto_sources


def test_ad10_doc_tu_file_chi_dinh(tmp_path: Path) -> None:
    rules = load_rules(_base(tmp_path, config_version='"t-1"', window_days="30"))
    assert (rules.config_version, rules.window_days, rules.auto_sources) == ("t-1", 30, ("a", "b"))


@pytest.mark.parametrize(
    "khoa", ["config_version", "window_days", "min_sample", "theta_core", "theta_common", "roles"]
)
def test_ad10_thieu_khoa_thi_bao_loi_tieng_viet(tmp_path: Path, khoa: str) -> None:
    with pytest.raises(ConfigError, match="thiếu") as exc:
        load_rules(_base(tmp_path, drop=khoa))
    assert khoa in str(exc.value)


@pytest.mark.parametrize(
    ("bang", "khoa"),
    [
        (SOURCES, "sources.auto"),
        (NOTE, "coverage_notes"),
        (CITY, "labels.city"),
        (ROLE, "labels.role"),
        (LEVEL, "labels.level"),
    ],
)
def test_ad10_thieu_bang_thi_bao_loi_tieng_viet(tmp_path: Path, bang: str, khoa: str) -> None:
    with pytest.raises(ConfigError, match="thiếu") as exc:
        load_rules(_write(tmp_path, BASE.replace(bang, "")))
    assert khoa in str(exc.value)


def test_ad10_gia_tri_sai_kieu_thi_bao_loi(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="window_days"):
        load_rules(_base(tmp_path, window_days="0"))
    with pytest.raises(ConfigError, match="sources.auto"):
        load_rules(_write(tmp_path, BASE.replace('auto = ["a", "b"]', 'auto = "a"')))


@pytest.mark.parametrize(
    ("swap", "khoa"),
    [
        ({"min_sample": "0"}, "min_sample"),
        ({"min_sample": "30.5"}, "min_sample"),
        ({"theta_core": "1.5"}, "theta_core"),
        ({"theta_common": '"x"'}, "theta_common"),
        ({"theta_common": "0.5"}, "theta_common"),
        ({"roles": "[]"}, "roles"),
        ({"roles": '["backend", "backend", "other"]'}, "roles"),
        ({"roles": '["all", "backend", "other"]'}, "roles"),
        ({"roles": '["backend", "frontend"]'}, "roles"),
    ],
)
def test_ad10_nguong_va_danh_sach_vai_tro_sai_thi_bao_loi(tmp_path: Path, swap: dict[str, str], khoa: str) -> None:
    with pytest.raises(ConfigError, match=khoa):
        load_rules(_base(tmp_path, **swap))


@pytest.mark.parametrize(
    ("bang", "moi", "khoa"),
    [
        (CITY, CITY.replace('"Đà Nẵng" = "da_nang"\n', ""), "labels.city"),
        (CITY, CITY.replace('"không xác định" = "unknown"\n', ""), "labels.city"),
        (CITY, CITY + '"Huế" = "hue"\n', "labels.city"),
        (LEVEL, LEVEL.replace('"không xác định" = "unknown"\n', '"Senior" = "senior"\n'), "labels.level"),
        (CITY, CITY.replace('"Khác" = "other"', '"Khác" = "unknown"'), "labels.city"),
        (ROLE, ROLE.replace('"Other" = "other"', '"Other" = "backend"'), "labels.role"),
    ],
)
def test_ad10_bang_nhan_thieu_ma_bat_buoc_hoac_trung_ma_thi_bao_loi(
    tmp_path: Path, bang: str, moi: str, khoa: str
) -> None:
    with pytest.raises(ConfigError, match=khoa):
        load_rules(_write(tmp_path, BASE.replace(bang, moi)))


def test_ad10_file_khong_ton_tai(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="tìm thấy"):
        load_rules(tmp_path / "khong-co.toml")


def test_ad10_auto_sources_khop_voi_scraper_ingest() -> None:
    tree = ast.parse((Path(__file__).resolve().parents[2] / "scraper" / "ingest.py").read_text(encoding="utf-8"))
    values = [
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "AUTO_SOURCES" for t in node.targets)
    ]
    assert len(values) == 1
    assert load_rules().auto_sources == tuple(values[0])


# ---------------------------------------------------------------- #93: khóa mới của phép tổng hợp


def test_ad10_khoa_moi_cua_tong_hop_thanh_pho() -> None:
    rules = load_rules()
    assert (rules.min_sample, rules.theta_core, rules.theta_common) == (30, 0.3, 0.1)
    assert rules.roles == (
        "embedded", "ai_ml", "data_engineer", "data_analyst", "qa", "devops", "mobile", "frontend", "backend", "other",
    )  # fmt: skip
    assert rules.config_version != "2026-11-06.1"


def test_ad10_ghi_chu_pham_vi_ba_ghi_chu_fr36_va_ghi_chu_so_nguon() -> None:
    notes = {n.code: n.text for n in load_rules().coverage_notes}
    assert list(notes) == ["n_sources", "posting_not_demand", "big_city_bias", "salary_disclosed_only"]
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên {n} nguồn."
    assert notes["posting_not_demand"] == "Tin tuyển dụng không đồng nghĩa với vị trí đang thực sự cần người."
    assert notes["big_city_bias"] == "Dữ liệu nghiêng về thành phố lớn và công ty lớn."
    assert notes["salary_disclosed_only"] == "Con số lương chỉ phản ánh những tin có công bố lương."


def test_ad10_bang_nhan_sang_ma_snake_case_dung_theo_issue() -> None:
    rules = load_rules()
    assert rules.city_codes == {
        "Hà Nội": "ha_noi", "TP.HCM": "ho_chi_minh", "Đà Nẵng": "da_nang", "Khác": "other", "không xác định": "unknown",
    }  # fmt: skip
    assert list(rules.city_codes.values()) == ["ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"]
    assert rules.role_codes == {
        "Embedded": "embedded", "AI/ML Engineer": "ai_ml", "Data Engineer": "data_engineer",
        "Data Analyst/BI": "data_analyst", "QA/Tester": "qa", "DevOps": "devops", "Mobile": "mobile",
        "Frontend": "frontend", "Backend": "backend", "Other": "other",
    }  # fmt: skip
    assert rules.level_codes == {
        "Intern": "intern", "Fresher": "fresher", "Junior": "junior", "Mid": "mid", "Senior": "senior",
        "Lead": "lead", "không xác định": "unknown",
    }  # fmt: skip
    assert set(rules.roles) == set(rules.role_codes.values())


def test_ad10_bang_nhan_khop_voi_luat_cua_bo_phan_loai() -> None:
    from haido_core.domain.classify import (
        NON_IT,
        OTHER_CITY,
        OTHER_ROLE,
        UNKNOWN,
        default_classify_config,
    )

    rules, cfg = load_rules(), default_classify_config()
    assert set(rules.city_codes) == {r.label for r in cfg.city_rules} | {OTHER_CITY, UNKNOWN}
    assert set(rules.role_codes) == {r.label for r in cfg.role_rules} | {OTHER_ROLE}
    assert NON_IT not in rules.role_codes
    assert set(rules.level_codes) == {r.label for r in cfg.seniority_rules} | {UNKNOWN}


# ---------------------------------------------------------------- #263: nguồn không bao giờ được đếm


def test_ad10_nguon_bi_loai_nam_trong_config_va_gom_linkedin() -> None:
    rules = load_rules()
    assert rules.excluded_sources == ("linkedin",)
    assert not set(rules.excluded_sources) & set(rules.auto_sources)


def test_ad10_nguon_bi_loai_doc_tu_file_chi_dinh(tmp_path: Path) -> None:
    assert load_rules(_base(tmp_path)).excluded_sources == ("x",)
    empty = _write(tmp_path, BASE.replace('excluded = ["x"]', "excluded = []"))
    assert load_rules(empty).excluded_sources == ()


def test_ad10_nguon_bi_loai_duoc_chuan_hoa_cat_khoang_trang_va_ha_chu_thuong(tmp_path: Path) -> None:
    rules = load_rules(_write(tmp_path, BASE.replace('excluded = ["x"]', 'excluded = ["LinkedIn ", " Foo"]')))
    assert rules.excluded_sources == ("linkedin", "foo")


def test_ad10_thieu_sources_excluded_thi_bao_loi_tieng_viet(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="thiếu") as exc:
        load_rules(_write(tmp_path, BASE.replace('excluded = ["x"]\n', "")))
    assert "sources.excluded" in str(exc.value)


@pytest.mark.parametrize("value", ['"linkedin"', "[1]", '[""]', '["  "]', '["x", "x"]', '["x", " X"]', '["a"]', '[" A "]'])
def test_ad10_sources_excluded_sai_thi_bao_loi(tmp_path: Path, value: str) -> None:
    with pytest.raises(ConfigError, match="sources.excluded"):
        load_rules(_write(tmp_path, BASE.replace('excluded = ["x"]', f"excluded = {value}")))


def test_ad10_config_version_da_tang_khi_them_nguon_bi_loai() -> None:
    assert load_rules().config_version not in {"2026-11-06.1", "2026-11-09.1"}


def test_ad10_thu_hang_nguon_cho_dai_dien_cum() -> None:
    rules = load_rules()
    assert rules.source_priority[0] == "itviec"
    assert "topcv" in rules.source_priority
    assert set(rules.auto_sources) <= set(rules.source_priority)


def test_ad10_config_version_da_tang_khi_them_gioi_han_cv() -> None:
    assert load_rules().config_version not in {"2026-11-06.1", "2026-11-09.1", "2026-11-10.1", "2026-11-10.2"}


def test_ad10_gioi_han_cv_mac_dinh_la_5_mib_pdf_va_docx() -> None:
    rules = load_rules()
    assert rules.cv_max_bytes == 5 * 1024 * 1024
    assert rules.cv_types == (PDF, DOCX)


def test_ad10_gioi_han_cv_doc_tu_file_chi_dinh(tmp_path: Path) -> None:
    rules = load_rules(_base(tmp_path, cv_max_bytes="1024", cv_types='["application/pdf"]'))
    assert (rules.cv_max_bytes, rules.cv_types) == (1024, (PDF,))


def test_ad10_cv_khong_doi_nguong_mau_theta_va_ghi_chu_pham_vi() -> None:
    rules = load_rules()
    assert (rules.min_sample, rules.theta_core, rules.theta_common) == (30, 0.3, 0.1)
    assert [n.code for n in rules.coverage_notes] == [
        "n_sources",
        "posting_not_demand",
        "big_city_bias",
        "salary_disclosed_only",
    ]


@pytest.mark.parametrize("khoa", ["cv_max_bytes", "cv_types"])
def test_ad10_thieu_khoa_cv_thi_bao_loi_tieng_viet(tmp_path: Path, khoa: str) -> None:
    with pytest.raises(ConfigError, match="thiếu") as exc:
        load_rules(_base(tmp_path, drop=khoa))
    assert khoa in str(exc.value)


@pytest.mark.parametrize(
    ("swap", "khoa"),
    [
        ({"cv_max_bytes": "0"}, "cv_max_bytes"),
        ({"cv_max_bytes": "-5"}, "cv_max_bytes"),
        ({"cv_max_bytes": "5.5"}, "cv_max_bytes"),
        ({"cv_max_bytes": '"5MB"'}, "cv_max_bytes"),
        ({"cv_max_bytes": "true"}, "cv_max_bytes"),
        ({"cv_types": "[]"}, "cv_types"),
        ({"cv_types": '"application/pdf"'}, "cv_types"),
        ({"cv_types": '["application/pdf", "application/pdf"]'}, "cv_types"),
        ({"cv_types": '["pdf"]'}, "cv_types"),
        ({"cv_types": '["application/pdf", 3]'}, "cv_types"),
        ({"cv_types": '["Application/PDF"]'}, "cv_types"),
        ({"cv_types": '["image/png"]'}, "cv_types"),
        ({"cv_types": '["application/pdf", "application/zip"]'}, "cv_types"),
        ({"cv_max_bytes": "52428801"}, "cv_max_bytes"),
    ],
)
def test_ad10_gioi_han_cv_sai_thi_bao_loi_tieng_viet(tmp_path: Path, swap: dict[str, str], khoa: str) -> None:
    with pytest.raises(ConfigError, match=khoa):
        load_rules(_base(tmp_path, **swap))


def test_ad10_cv_max_bytes_dung_50_mib_van_duoc(tmp_path: Path) -> None:
    rules = load_rules(_base(tmp_path, cv_max_bytes=str(50 * 1024 * 1024)))
    assert rules.cv_max_bytes == 50 * 1024 * 1024
