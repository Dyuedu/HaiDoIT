"""Nơi làm việc của tin, gán ở bước ingest (#285).

Revision ID: 0008_haido_fact_city
Revises: 0007_haido_classify_at_ingest
Create Date: 2026-11-13 12:00:00

`job_posting_facts.city`: nhãn nơi của bộ phân loại (34 tỉnh, thành sau 1/7/2025, `Remote`, `Nước ngoài`,
`không xác định`), đọc từ trường địa điểm và dòng địa chỉ của JD lúc ingest. `null` ở hàng cũ; `aggregate` khi đó phân
loại từ `location_text`. Hạ cấp bỏ cột.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008_haido_fact_city"
down_revision: str | Sequence[str] | None = "0007_haido_classify_at_ingest"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"


def upgrade() -> None:
    op.add_column("job_posting_facts", sa.Column("city", sa.Text()), schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("job_posting_facts", "city", schema=SCHEMA)
