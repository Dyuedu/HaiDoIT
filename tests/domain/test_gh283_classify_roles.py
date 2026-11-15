"""#283 — vai trò và chức danh con đọc cả chức danh và nội dung tin (luật, không gọi mô hình).

Văn bản là JD ngắn tự viết. Mỗi lỗi đã thấy khi tự đọc tin thật (specs/283-phan-loai-tu-jd/research.md)
có một scenario ở đây.
"""

import pytest

from haido_core.config import load_classify_config
from haido_core.domain.classify import NON_IT, RuleClassifier
from haido_core.domain.mapping import VocabularyMapper
from haido_core.domain.posting_text import requirement_text, skill_counts
from haido_core.domain.registry import PostingFacts
from haido_core.vocab.skills import load_vocabulary

CFG = load_classify_config()
VOCAB = load_vocabulary()
MAPPER = VocabularyMapper(VOCAB)
CLF = RuleClassifier(CFG)


def tin(title: str, text: str = "", *, source: str = "topcv", seniority: str | None = None,
        years: float | None = None) -> PostingFacts:
    body = requirement_text(text, CFG)
    skills = tuple(sorted(skill_counts(body, VOCAB, MAPPER).items()))
    return PostingFacts(title, source, None, seniority, None, text=body, skills=skills, years_min=years)


def role(title: str, text: str = "", **kw: object) -> str:
    return CLF.classify(tin(title, text, **kw)).role  # type: ignore[arg-type]


FULLSTACK_JD = (
    "Yêu cầu: React, Next.js, Redux, HTML, CSS, TypeScript; Node.js, NestJS, PostgreSQL, Docker, REST API, Redis."
)


@pytest.mark.parametrize(
    ("title", "text", "expected"),
    [
        ("Senior Software Engineer (Java)", "", "Backend"),
        ("Lập trình viên", FULLSTACK_JD, "Fullstack"),
        ("Lập trình viên", "Yêu cầu: React, Redux, CSS, HTML, JavaScript, Tailwind.", "Frontend"),
        ("Kỹ sư AI", "", "AI/ML Engineer"),
        ("AI Agent Engineer (Python, LLM)", "", "AI/ML Engineer"),
        ("LLM Engineer", "", "AI/ML Engineer"),
        ("Data Scientist", "", "Data Scientist"),
        ("Thực tập sinh Khoa học dữ liệu", "", "Data Scientist"),
        ("Product Owner (OCR/AI)", "", "BA/PO/PM"),
        ("Phụ trách thương mại hóa sản phẩm AI", "", NON_IT),
        ("Sales Executive (AI SaaS)", "", NON_IT),
        ("Business Analyst", "", "BA/PO/PM"),
        ("Scrum Master", "", "BA/PO/PM"),
        ("Head of Product, Zing MP3", "", "BA/PO/PM"),
        ("(Senior) Product Specialist, ZTransfer", "", "BA/PO/PM"),
        ("Chuyên viên Khách hàng Doanh nghiệp - Khu vực Sơn Tây, Ba Vì - Hà Nội", "", NON_IT),
        ("CyberSecurity Engineer", "", "Security"),
        ("Kỹ Sư An Ninh Thông Tin", "", "Security"),
        ("Penetration Tester", "", "Security"),
        ("Nhân viên IT Helpdesk", "", "Hạ tầng/IT support"),
        ("Quản trị mạng", "", "Hạ tầng/IT support"),
        ("Senior System Engineer", "", "Hạ tầng/IT support"),
        ("UI/UX Designer", "", "UI/UX"),
        ("Graphic & Motion Designer", "Yêu cầu: Figma, Photoshop, Illustrator, After Effects.", NON_IT),
        ("2D Game Artist (Photoshop/Illustrator)", "Yêu cầu: Unity, Spine, Photoshop.", NON_IT),
        ("Unity Game Developer", "", "Game"),
        ("Unity Technical Artist", "", "Game"),
        ("Kỹ Sư Quy Hoạch Thiết Kế Mạng Vô Tuyến Di Động 4G, 5G", "", NON_IT),
        ("Nhân Viên Lập Trình CNC", "", NON_IT),
        ("Product Developer Manager", "Yêu cầu: kinh nghiệm phát triển sản phẩm may mặc, giày dép.", NON_IT),
        ("Product Owner (E-Commerce/ SaaS)", "", "BA/PO/PM"),
        ("Nhân viên kinh doanh phần mềm", "", NON_IT),
        ("Flutter Mobile Developer", "", "Mobile"),
        ("User Acquisition Executive (Mobile Game)", "", NON_IT),
        ("Embedded Software Engineer", "", "Embedded"),
        ("Data Engineer", "", "Data Engineer"),
        ("Data Analyst", "", "Data Analyst/BI"),
        ("DevOps Engineer", "", "DevOps"),
        ("Automation Tester", "", "QA/Tester"),
    ],
)
def test_gh283_vai_tro_tu_chuc_danh_va_noi_dung(title: str, text: str, expected: str) -> None:
    assert role(title, text) == expected


@pytest.mark.parametrize(
    ("title", "text", "source", "expected"),
    [
        # Đợt 2 (mẫu tự gán nhãn, tools/classify_eval): TopDev đăng cả tin ngân hàng, xây dựng.
        ("Chuyên viên Khách hàng Doanh nghiệp (1-3 năm Kinh nghiệm) - Quận 12", "", "topdev", NON_IT),
        ("Site Engineer", "Mô tả công việc\nGiám sát công trình xây dựng.", "topdev", NON_IT),
        ("Quality Control Specialist (QC/Tester, Jira, Postman)", "Yêu cầu: viết test case, Postman, Jira.", "itviec",
         "QA/Tester"),
        ("CVCC Phát triển mạng lưới QR (Senior QR Network Development)", "Chỉ tiêu kinh doanh cho vay.", "topdev",
         NON_IT),
        ("Systems Administrator & CSV Support Trainee", "Yêu cầu: Windows, Microsoft Office.", "vietnamworks",
         "Hạ tầng/IT support"),
        ("Quản Trị Viên Máy Chủ", "Yêu cầu: Linux server, Nginx, MySQL.", "topcv", "Hạ tầng/IT support"),
        ("[Hà Nội] CV/CVCC Quản Lý Chất Lượng và Tuân Thủ (QA)", "", "vietnamworks", "QA/Tester"),
        ("Senior Applied AI Scientist, Zalo Photos", "", "zalo", "AI/ML Engineer"),
        ("Nhân Viên UI & Graphic Designer (Ngành Game)", "", "topcv", "UI/UX"),
        ("Chuyên Viên AI Video Editor Và Design", "Yêu cầu: CapCut, Premiere, Photoshop.", "topcv", NON_IT),
        ("Giám Đốc Công Nghệ (CTO)", "Yêu cầu: quản lý đội ngũ, chiến lược công nghệ.", "topcv", "Other"),
        ("Solutions Architect", "Yêu cầu: trình bày giải pháp cho khách hàng.", "itviec", "Other"),
    ],
)
def test_gh283_loi_tu_mau_tu_gan_nhan(title: str, text: str, source: str, expected: str) -> None:
    assert role(title, text, source=source) == expected


def test_gh283_test_engineer_phong_thu_nghiem_khong_thuoc_it() -> None:
    jd = "Mô tả công việc\nThử nghiệm, kiểm tra sản phẩm điện, điện tử theo tiêu chuẩn.\nYêu cầu\nTốt nghiệp điện tử."
    assert role("Test Engineer (Kỹ Sư Phòng Thử Nghiệm)", jd) == NON_IT
    assert role("Tester Intern") == "QA/Tester"


def test_gh283_khong_co_cum_vai_tro_can_du_ky_nang_ky_thuat() -> None:
    many = "Yêu cầu: Python, Docker, Kubernetes, Terraform, AWS, CI/CD, Linux, Prometheus."
    assert role("Chuyên viên", many) == "DevOps"
    assert role("Chuyên viên", "Yêu cầu: Excel, giao tiếp tốt, tiếng Anh.") == NON_IT


def test_gh283_nguon_chi_dang_tin_it_khong_co_tu_khoa_van_la_other() -> None:
    assert role("Chuyên viên sản phẩm", source="itviec") == "Other"
    assert role("Chuyên viên sản phẩm", source="zalo") == NON_IT


@pytest.mark.parametrize(
    ("title", "expected_role", "expected_branch"),
    [
        ("Business Analyst", "BA/PO/PM", "Business Analyst"),
        ("Product Owner", "BA/PO/PM", "Product Owner"),
        ("IT Project Manager", "BA/PO/PM", "Project Manager"),
        ("SAP FICO Consultant", "BA/PO/PM", "ERP/SAP consultant"),
        ("IT Helpdesk", "Hạ tầng/IT support", "Helpdesk/Support"),
        ("Network Engineer", "Hạ tầng/IT support", "Network"),
        ("System Administrator", "Hạ tầng/IT support", "System Admin"),
        ("Automation Tester", "QA/Tester", "Automation"),
        ("Pentester", "Security", "Pentest"),
    ],
)
def test_gh283_chuc_danh_con(title: str, expected_role: str, expected_branch: str) -> None:
    result = CLF.classify(tin(title))
    assert (result.role, result.branch) == (expected_role, expected_branch)


def test_gh283_khong_khop_chuc_danh_con_thi_none() -> None:
    assert CLF.classify(tin("Backend Developer")).branch is None


def test_gh283_cung_dau_vao_cung_nhan_khong_phu_thuoc_thu_tu_lo() -> None:
    a, b, c = tin("Lập trình viên", FULLSTACK_JD), tin("Data Scientist"), tin("Kế toán")
    first = CLF.classify([a, b, c])
    again = CLF.classify([c, a, b])
    assert first == (again[1], again[2], again[0])
    assert CLF.classify(a) == first[0]
