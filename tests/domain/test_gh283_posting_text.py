"""#283 — đọc văn bản JD trong bộ nhớ: mục yêu cầu, lượt nhắc kỹ năng, số năm.

Văn bản trong test là JD ngắn tự viết, không phải JD thật.
"""

from haido_core.config import load_classify_config
from haido_core.domain.mapping import VocabularyMapper
from haido_core.domain.posting_text import (
    find_mentions,
    fold,
    requirement_text,
    resolve_years,
    skill_counts,
)
from haido_core.vocab.skills import load_vocabulary

CFG = load_classify_config()
VOCAB = load_vocabulary()
MAPPER = VocabularyMapper(VOCAB)


def _skills(text: str) -> dict[str, int]:
    return skill_counts(requirement_text(text, CFG), VOCAB, MAPPER)


def test_gh283_fold_bo_dau_chu_thuong_gop_khoang_trang() -> None:
    assert fold("  Kiểm  Thử\tĐồng bộ ") == "kiem thu dong bo"
    assert fold(None) == ""


def test_gh283_giu_muc_yeu_cau_va_nhiem_vu_bo_quyen_loi_va_gioi_thieu() -> None:
    jd = (
        "Về chúng tôi\nCông ty hàng đầu về Machine Learning.\n"
        "Mô tả công việc\nPhát triển API bằng Docker.\n"
        "Yêu cầu ứng viên\nThành thạo Python. Biết Python nâng cao.\n"
        "Quyền lợi\nĐược học Machine Learning miễn phí.\n"
        "Địa điểm làm việc\nTòa nhà Kubernetes, Hà Nội\n"
    )
    text = requirement_text(jd, CFG)
    assert "docker" in text
    assert "python" in text
    assert "machine learning" not in text
    assert "kubernetes" not in text
    assert _skills(jd) == {"docker": 1, "python": 2}


def test_gh283_khong_co_tieu_de_muc_thi_giu_het() -> None:
    assert _skills("Cần biết React và TypeScript, có Git.") == {"react": 1, "typescript": 1, "git": 1}


def test_gh283_cat_van_ban_qua_dai() -> None:
    long_text = "a " * (CFG.max_text_chars) + "Python"
    assert len(requirement_text(long_text, CFG)) <= CFG.max_text_chars
    assert "python" not in _skills(long_text)


def test_gh283_khoa_hoc_may_tinh_khong_phai_hoc_may() -> None:
    assert "machine_learning" not in _skills("Tốt nghiệp chuyên ngành Khoa học máy tính hoặc CNTT.")
    assert _skills("Có kinh nghiệm học máy và Machine Learning.")["machine_learning"] == 2


def test_gh283_chu_tieng_viet_khong_bi_doc_nham_thanh_ky_nang() -> None:
    skills = _skills("Chăm sóc khách hàng, sắp xếp công việc, làm việc ở sàn, lần đầu đi làm, PIC dự án.")
    assert not {"siem", "sap"} & set(skills)


def test_gh283_cum_dai_truoc_va_ma_ghep() -> None:
    assert _skills("Thành thạo C/C++.") == {"c": 1, "cpp": 1}
    skills = _skills("Lập trình ASP.NET Core và Spring Boot.")
    assert skills["dotnet"] == 1
    assert skills["spring_boot"] == 1
    assert "spring" not in skills


def test_gh283_song_ngu_ve_mot_ma_va_dem_moi_luot() -> None:
    assert _skills("Kiểm thử tự động, automation testing, kiem thu tu dong.") == {"automation_testing": 3}


def test_gh283_tim_luot_nhac_neo_vi_tri_tren_van_ban_da_bo_dau() -> None:
    text = fold("Biết Python")
    mentions = find_mentions(text, VOCAB)
    assert [(m.text, text[m.start : m.end]) for m in mentions] == [("python", "python")]


def test_gh283_so_thang_cua_nguon_thang() -> None:
    src = '{"@type": "OccupationalExperienceRequirements", "monthsOfExperience": 24}'
    assert resolve_years(src, 3.0, "", CFG) == 2.0
    assert resolve_years("no requirements", None, "", CFG) == 0.0


def test_gh283_gia_tri_buoc_trich_truoc_luat() -> None:
    assert resolve_years(None, 3.0, fold("Tối thiểu 5 năm kinh nghiệm"), CFG) == 3.0


def test_gh283_khong_yeu_cau_kinh_nghiem_la_0_khi_buoc_trich_de_trong() -> None:
    assert resolve_years(None, None, fold("Không yêu cầu kinh nghiệm, được đào tạo."), CFG) == 0.0
    assert resolve_years(None, None, fold("No experience required."), CFG) == 0.0


def test_gh283_lay_yeu_cau_chinh_khong_lay_so_nho_nhat() -> None:
    text = fold("Tối thiểu 5 năm kinh nghiệm, trong đó ít nhất 2 năm quản lý đội nhóm.")
    assert resolve_years(None, None, text, CFG) == 5.0
    assert resolve_years(None, None, fold("Có từ 3–5 năm kinh nghiệm Java."), CFG) == 3.0
    assert resolve_years(None, None, fold("At least 4 years of experience with Go."), CFG) == 4.0


def test_gh283_so_nam_ngoai_ngu_canh_kinh_nghiem_bi_bo() -> None:
    assert resolve_years(None, None, fold("Công ty thành lập 10 năm, hợp đồng 2 năm."), CFG) is None
    assert resolve_years(None, None, "", CFG) is None
