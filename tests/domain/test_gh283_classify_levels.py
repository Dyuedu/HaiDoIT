"""#283 — cấp: chức danh → chữ cấp của nguồn → số năm (bảng #134) → không xác định."""

import pytest

from haido_core.config import load_classify_config
from haido_core.domain.classify import RuleClassifier
from haido_core.domain.registry import PostingFacts

CLF = RuleClassifier(load_classify_config())


def level(title: str, *, seniority: str | None = None, years: float | None = None, text: str = "") -> str:
    return CLF.classify(PostingFacts(title, "topcv", None, seniority, None, text=text, years_min=years)).seniority


@pytest.mark.parametrize(
    ("years", "expected"),
    [(0.0, "Fresher"), (0.5, "Fresher"), (1.0, "Junior"), (1.5, "Junior"), (2.0, "Mid"), (3.0, "Mid"),
     (4.9, "Mid"), (5.0, "Senior"), (12.0, "Senior")],
)
def test_gh283_cap_tu_so_nam_theo_bang_134(years: float, expected: str) -> None:
    assert level("Backend Developer", years=years) == expected


def test_gh283_chuc_danh_thang_so_nam_va_khong_ra_intern_lead_tu_so_nam() -> None:
    assert level("Senior Backend Developer", years=1.0) == "Senior"
    assert level("Backend Intern", years=3.0) == "Intern"
    assert level("Backend Developer", years=15.0) == "Senior"


def test_gh283_chu_cap_cua_nguon_truoc_so_nam() -> None:
    assert level("Backend Developer", seniority="Fresher/Entry level", years=4.0) == "Fresher"
    assert level("Backend Developer", seniority="Thực tập, Mới tốt nghiệp") == "Intern"


def test_gh283_non_manager_cua_vietnamworks_khong_cho_cap() -> None:
    assert level("Backend Developer", seniority="Experienced (non-manager)") == "không xác định"
    assert level("Backend Developer", seniority="Experienced (non-manager)", years=3.0) == "Mid"


def test_gh283_product_manager_khong_phai_cap_lead() -> None:
    assert level("Product Manager") != "Lead"
    assert level("Project Manager", years=3.0) == "Mid"
    for title in ("Head of Product", "Tech Lead", "Trưởng nhóm Java", "Engineering Manager", "Giám đốc CNTT"):
        assert level(title) == "Lead", title


def test_gh283_khong_co_gi_thi_khong_xac_dinh() -> None:
    assert level("Backend Developer") == "không xác định"
