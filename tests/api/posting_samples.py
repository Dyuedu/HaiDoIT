"""Chữ dán mẫu và mã kỹ năng dùng chung cho test của tin dán (#230).

Bản giả của `POST /api/v1/posting-reads` chọn kết quả từ chữ dán (xem `haido_api/posting_read.py`):
ngắn hơn 200 ký tự là `too_short`; không có dấu IT thì `not_it` khi có dấu tin tuyển dụng, `not_posting` khi không;
có `đặt cọc` hay `deposit` là tin có phí; có `devops` hay `kubernetes` là tin DevOps (nhánh Cloud, đã có tin thu thập khớp);
còn lại là tin Backend Junior.
"""

from typing import Any

SENTINEL = "ZXQ-CHU-BI-MAT-9917"
"""Chuỗi không được xuất hiện ở bất kỳ log, lỗi hay trạng thái nào (AD-11)."""

BACKEND_TEXT = (
    "Công ty Alpha Soft tuyển Backend Developer (Junior). Yêu cầu: 1 năm kinh nghiệm Java, Spring Boot, SQL, Git; "
    "biết Docker, MySQL là lợi thế; ưu tiên có Kafka, Linux và Quarkus. Lương 10-18 triệu. Gửi CV về hr@alphasoft.vn. "
    + SENTINEL
)
FEE_TEXT = (
    "Tuyển lập trình viên Java làm việc tại nhà, thu nhập cao, không cần kinh nghiệm. Ứng viên đặt cọc 500.000đ "
    "phí hồ sơ để giữ chỗ. Liên hệ Zalo hoặc Telegram để nhận việc ngay, không nêu tên công ty. " + SENTINEL
)
NOT_POSTING_TEXT = (
    "Hôm nay mình nấu canh chua cá lóc với dứa, cà chua và bạc hà, thêm chút rau om cho thơm. Món này ăn với cơm "
    "trắng rất hợp, cả nhà ai cũng thích. Cuối tuần mình sẽ làm lại, nhớ ướp cá trước nửa tiếng. " + SENTINEL
)
SHORT_TEXT = "Tuyển Backend Java Junior, lương 12 triệu. " + SENTINEL
NOT_IT_TEXT = (
    "Công ty Gamma tuyển dụng kế toán tổng hợp, yêu cầu 2 năm kinh nghiệm làm sổ sách, thành thạo Excel và các chuẩn mực "
    "kế toán. Mức lương 12-15 triệu, quyền lợi đầy đủ theo luật lao động, thưởng cuối năm. Ứng tuyển bằng cách gửi CV "
    "về phòng nhân sự trước cuối tháng. " + SENTINEL
)
CLOUD_TEXT = (
    "Beta Cloud tuyển DevOps Engineer (Mid), nhánh Cloud. Yêu cầu: 3 năm kinh nghiệm AWS, Kubernetes, Docker, Terraform, "
    "Linux, CI/CD; ưu tiên có Pulumi. Lương thỏa thuận theo năng lực. Gửi CV về hr@betacloud.vn. " + SENTINEL
)

POSTING_SKILLS = ["java", "sql", "spring_boot", "git", "docker", "mysql", "kafka", "linux"]
"""Kỹ năng của tin Backend Junior giả: 4 core, 2 common, 2 specific ở ô `vn.backend.junior`."""
HAVE_16_OF_18 = ["java", "sql", "spring_boot", "git", "docker", "mysql"]
"""Ví dụ FR-28: 4/4 core + 2/2 common + 0/2 specific = 16/18 = 89%."""


CLOUD_SKILLS = ["docker", "kubernetes", "aws", "terraform", "linux", "ci_cd"]
"""Kỹ năng của tin DevOps giả. Ô `vn.devops` (cấp `mid` quay về ô mọi cấp)."""

SCREEN_ONLY_FIELDS: frozenset[str] = frozenset(
    {"unrecognised", "fee_mentions", "contact_quotes", "collected", "model_id", "prompt_version", "vocab_version", "reason", "is_posting"}
)
"""Trường của `PostingReadData` chỉ hiện trên màn, không vào query (chữ nguyên văn hoặc truy vết). `collected` đi vào
query chỉ qua hai số `collected_reposts` và `collected_snapshots`."""
QUERY_FIELDS: frozenset[str] = frozenset(
    {
        "role", "level", "branch", "skills", "years_min", "salary", "salary_non_numeric", "company_named", "contacts",
        "duties_described", "title_level",
    }
)  # fmt: skip
"""Trường của `PostingReadData` mà bước hai nhận (dưới dạng mã hoặc số). `fee_mentions` đi vào qua số `fees`."""


def query_from_read(data: dict[str, Any], *, have: list[str] | None = None) -> dict[str, str]:
    """Dựng query của bước hai từ `data` của bước một, đúng như `web/lib/posting.ts` (`postingCheckUrl`): chỉ mã và số."""
    query: dict[str, str] = {"role": data["role"], "level": data["level"]}
    if have:
        query["have"] = csv(have)
    if data["branch"] is not None:
        query["branch"] = data["branch"]
    if data["skills"]:
        query["skills"] = csv([s["code"] for s in data["skills"]])
    if data["years_min"] is not None:
        query["years_min"] = str(data["years_min"])
    if data["salary"] is not None:
        salary = data["salary"]
        for key in ("min", "max"):
            if salary[key] is not None:
                query[f"salary_{key}"] = str(salary[key])
        query["salary_currency"] = salary["currency"]
        query["salary_period"] = salary["period"]
    if data["salary_non_numeric"]:
        query["salary_non_numeric"] = "true"
    query["company_named"] = str(data["company_named"]).lower()
    if data["contacts"]:
        query["contacts"] = csv(data["contacts"])
    if data["fee_mentions"]:
        query["fees"] = str(len(data["fee_mentions"]))
    query["duties_described"] = str(data["duties_described"]).lower()
    if data["title_level"] is not None:
        query["title_level"] = data["title_level"]
    if data["collected"] is not None:
        query["collected_reposts"] = str(data["collected"]["repost_count"])
        query["collected_snapshots"] = str(data["collected"]["snapshots_seen"])
    return query


def csv(codes: list[str]) -> str:
    return ",".join(codes)
