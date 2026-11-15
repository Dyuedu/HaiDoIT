"""#285 — nơi làm việc: 34 tỉnh, thành sau 1/7/2025, dòng địa chỉ của JD, Remote, Nước ngoài."""

import pytest

from haido_core.config import load_classify_config
from haido_core.domain.classify import UNKNOWN, RuleClassifier
from haido_core.domain.posting_text import address_text
from haido_core.domain.registry import PostingFacts

CFG = load_classify_config()
CLF = RuleClassifier(CFG)


def city(location: str | None, jd: str = "") -> str:
    facts = PostingFacts("Backend Developer", "topcv", None, None, location, address_text=address_text(jd, CFG))
    return CLF.classify(facts).city


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ("Hà Nội", "Hà Nội"),
        ("Hồ Chí Minh", "TP.HCM"),
        ("Bình Dương", "TP.HCM"),
        ("Thủ Dầu Một, Bình Dương", "TP.HCM"),
        ("Vũng Tàu", "TP.HCM"),
        ("Quảng Nam", "Đà Nẵng"),
        ("Hội An", "Đà Nẵng"),
        ("Hải Dương", "Hải Phòng"),
        ("Bắc Giang", "Bắc Ninh"),
        ("Nam Định", "Ninh Bình"),
        ("Long An", "Tây Ninh"),
        ("Vĩnh Phúc", "Phú Thọ"),
        ("Vĩnh Long", "Vĩnh Long"),
        ("Phường Vỹ Dạ, Huế", "Huế"),
        ("Nha Trang", "Khánh Hòa"),
        ("Biên Hòa, Đồng Nai", "Đồng Nai"),
        ("Cần Thơ", "Cần Thơ"),
        ("Đà Nẵng / Hà Nội", "Đà Nẵng"),
    ],
)
def test_gh285_tinh_cu_quy_ve_tinh_moi(location: str, expected: str) -> None:
    assert city(location) == expected


def test_gh285_bang_tinh_co_dung_34_tinh() -> None:
    assert len(CFG.city_rules) == 34
    assert len({r.label for r in CFG.city_rules}) == 34


def test_gh285_location_trong_thi_doc_dong_dia_chi() -> None:
    jd = "Mô tả công việc\nPhát triển API.\nĐịa điểm làm việc: Tòa nhà X, Cầu Giấy, Hà Nội\n"
    assert city(None, jd) == "Hà Nội"
    jd2 = "Địa điểm làm việc:\n- Tầng 5, Quận 1, TP. Hồ Chí Minh\n"
    assert city("", jd2) == "TP.HCM"


def test_gh285_chu_ngoai_dong_dia_chi_khong_dat_noi() -> None:
    jd = "Về chúng tôi\nCông ty thành lập tại Đà Nẵng năm 2010.\nYêu cầu\nPython."
    assert city(None, jd) == UNKNOWN


def test_gh285_truong_location_thang_dia_chi_jd() -> None:
    assert city("Hà Nội", "Địa chỉ: Quận 7, Hồ Chí Minh") == "Hà Nội"


def test_gh285_remote_chi_khi_khong_neu_tinh() -> None:
    assert city(None, "Hình thức làm việc: Remote, làm việc từ xa toàn thời gian.\nĐịa điểm: Remote") == "Remote"
    assert city("Remote", "Địa điểm làm việc: Cầu Giấy, Hà Nội") == "Hà Nội"


def test_gh285_nuoc_ngoai() -> None:
    assert city("Quốc tế") == "Nước ngoài"
    assert city("Nước Ngoài") == "Nước ngoài"
    assert city(None, "Địa điểm làm việc: Tokyo, Nhật Bản") == "Nước ngoài"
    assert city("Hà Nội", "Địa điểm làm việc: onsite Tokyo, Nhật Bản") == "Hà Nội"


def test_gh285_khong_co_gi_thi_khong_xac_dinh() -> None:
    assert city(None) == UNKNOWN
    assert city("Toàn quốc") == UNKNOWN


def test_gh285_address_text_chi_lay_dong_dia_chi() -> None:
    jd = "Giới thiệu\nVăn phòng đẹp.\nYêu cầu\nPython ở Hà Nội.\nĐịa chỉ: 12 Duy Tân\nCầu Giấy, Hà Nội\nQuyền lợi\nLương"
    text = address_text(jd, CFG)
    assert "duy tan" in text
    assert "cau giay, ha noi" in text
    assert "python" not in text
