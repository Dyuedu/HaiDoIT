"""Nhãn phân loại của tin, gán ở bước ingest (#283).

Revision ID: 0007_haido_classify_at_ingest
Revises: 0006_haido_years_filter
Create Date: 2026-11-13 00:00:00

`job_posting_facts` có thêm năm cột, đều cho phép `null` (hàng cũ không có nhãn):

- `role`, `branch`, `seniority`: nhãn vai trò, chức danh con, cấp của bộ phân loại (`config/classify.toml`).
- `skills`: object mã kỹ năng → số lượt nhắc trong mục yêu cầu và nhiệm vụ. Chỉ mã, không có chuỗi nguyên văn.
- `classify_version`: phiên bản luật đã dùng.

Không có cột văn bản JD (DoD dòng 9). Hạ cấp bỏ năm cột; `aggregate` quay về phân loại từ trường đóng.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0007_haido_classify_at_ingest"
down_revision: str | Sequence[str] | None = "0006_haido_years_filter"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"
TEXT_COLUMNS = ("role", "branch", "seniority", "classify_version")


def upgrade() -> None:
    for name in TEXT_COLUMNS[:3]:
        op.add_column("job_posting_facts", sa.Column(name, sa.Text()), schema=SCHEMA)
    op.add_column("job_posting_facts", sa.Column("skills", JSONB()), schema=SCHEMA)
    op.add_column("job_posting_facts", sa.Column("classify_version", sa.Text()), schema=SCHEMA)


def downgrade() -> None:
    for name in (*TEXT_COLUMNS, "skills"):
        op.drop_column("job_posting_facts", name, schema=SCHEMA)
