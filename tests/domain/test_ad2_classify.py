"""AD-2 — phép phân loại tất định (Story 1.20)."""

from haido_core.domain.classify import (
    NON_IT,
    OTHER_ROLE,
    RuleClassifier,
    counts_in_aggregate,
    default_classify_config,
    exclusion_by_source,
)
from haido_core.domain.registry import Classification, PostingFacts

CONFIG = default_classify_config()
CLF = RuleClassifier(CONFIG)


def _tin(
    title: str,
    *,
    source: str = "vietnamworks",
    category: str | None = None,
    seniority: str | None = None,
    location: str | None = None,
) -> PostingFacts:
    return PostingFacts(title, source, category, seniority, location)


def test_ad2_data_tach_ba_nhanh_va_embedded_khong_vao_other() -> None:
    assert CLF.classify(_tin("Data Engineer")).role == "Data Engineer"
    assert CLF.classify(_tin("Data Analyst")).role == "Data Analyst/BI"
    assert CLF.classify(_tin("Machine Learning Engineer")).role == "AI/ML Engineer"
    assert CLF.classify(_tin("Embedded Software Engineer")).role == "Embedded"
    assert CLF.classify(_tin("Embedded Software Engineer")).role != OTHER_ROLE


def test_ad2_khong_thuoc_it_bi_loai_va_ty_le_theo_nguon() -> None:
    ke_toan = CLF.classify(_tin("Kế toán tổng hợp", source="momo"))
    backend = CLF.classify(_tin("Backend Engineer", source="momo", category="finance"))
    assert ke_toan.role == NON_IT
    assert backend.role == "Backend"
    assert counts_in_aggregate(ke_toan) is False
    assert counts_in_aggregate(backend) is True
    report = exclusion_by_source([("momo", ke_toan), ("momo", backend), ("itviec", backend)])
    assert report == (
        type(report[0])(source="itviec", excluded=0, total=1),
        type(report[0])(source="momo", excluded=1, total=2),
    )


def test_ad2_nhieu_thanh_pho_lay_cum_xuat_hien_truoc() -> None:
    assert CONFIG.multi_city == "first_phrase"
    assert CLF.classify(_tin("Backend", location="Da Nang / Ha Noi")).city == "Đà Nẵng"
    assert CLF.classify(_tin("Backend", location="Hà Nội và TP.HCM")).city == "Hà Nội"
    # #285: mỗi tỉnh có nhãn riêng (không còn "Khác"); Remote là một nơi riêng.
    assert CLF.classify(_tin("Backend", location="Hải Phòng")).city == "Hải Phòng"
    assert CLF.classify(_tin("Backend", location="Remote")).city == "Remote"
    assert CLF.classify(_tin("Backend", location=None)).city == "không xác định"


def test_ad2_cap_bac_uu_tien_chu_nguon_ghi() -> None:
    labeled = CLF.classify(_tin("Senior Backend", seniority="Junior"))
    assert labeled.seniority == "Junior"
    assert CLF.classify(_tin("Backend")).seniority == "không xác định"
    assert CLF.classify(_tin("Intern Backend")).seniority == "Intern"


def test_ad2_cung_dau_vao_cung_nhan_va_lo() -> None:
    tin = _tin("Java Backend", source="itviec", seniority="Fresher", location="Ha Noi")
    one = CLF.classify(tin)
    assert one == CLF.classify(tin)
    assert isinstance(one, Classification)
    assert one.branch is None
    assert one.role == "Backend"
    assert one.city == "Hà Nội"
    batch = CLF.classify([tin, tin])
    assert batch == (one, one)
    assert CLF.classify(()) == ()


def test_ad2_nguon_it_khong_co_tu_khoa_la_other() -> None:
    assert CLF.classify(_tin("Chuyên viên sản phẩm", source="itviec")).role == OTHER_ROLE
    assert CLF.classify(_tin("Chuyên viên sản phẩm", source="zalo")).role == NON_IT
