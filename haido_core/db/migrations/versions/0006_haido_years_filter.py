"""Số năm kinh nghiệm tối thiểu của tin và ô theo mốc số năm của bản đồ (#280).

Revision ID: 0006_haido_years_filter
Revises: 0005_haido_city_share_level
Create Date: 2026-11-12 00:00:00

- `job_posting_facts.years_min`: số năm tối thiểu tin yêu cầu, chép từ `jobs.years_experience_min` của scraper;
  `null` là tin không ghi.
- `stat_cells` và `stat_city_shares` có thêm cột `years` trong khóa chính: `any` (mọi số năm) hoặc mã mốc (`0`,
  `1`, ...; xem `years_options` trong `config/rules.toml`). Hàng cũ là số của mọi số năm nên nhận `any`.
- `stat_cells.years_unstated`: số cụm của (vai trò, cấp, phạm vi) không ghi số năm. Hàng cũ nhận 0.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_haido_years_filter"
down_revision: str | Sequence[str] | None = "0005_haido_city_share_level"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"
CELLS_PK = "stat_cells_pkey"
SHARES_PK = "stat_city_shares_pkey"
CELLS_KEY = ["snapshot_id", "role", "branch", "seniority", "scope"]
SHARES_KEY = ["snapshot_id", "role", "seniority", "city"]


def upgrade() -> None:
    op.add_column("job_posting_facts", sa.Column("years_min", sa.Float(precision=53)), schema=SCHEMA)
    # server_default của `years` và `years_unstated` chỉ để lấp hàng cũ; bỏ ngay sau đó để bước ghi buộc phải nêu.
    for table, pk, key in (("stat_cells", CELLS_PK, CELLS_KEY), ("stat_city_shares", SHARES_PK, SHARES_KEY)):
        op.add_column(table, sa.Column("years", sa.Text(), nullable=False, server_default="any"), schema=SCHEMA)
        op.alter_column(table, "years", server_default=None, schema=SCHEMA)
        op.drop_constraint(pk, table, schema=SCHEMA, type_="primary")
        op.create_primary_key(pk, table, [*key[:-1], "years", key[-1]], schema=SCHEMA)
    op.add_column(
        "stat_cells", sa.Column("years_unstated", sa.Integer(), nullable=False, server_default="0"), schema=SCHEMA
    )
    op.alter_column("stat_cells", "years_unstated", server_default=None, schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("stat_cells", "years_unstated", schema=SCHEMA)
    for table, pk, key in (("stat_cells", CELLS_PK, CELLS_KEY), ("stat_city_shares", SHARES_PK, SHARES_KEY)):
        op.execute(sa.text(f"DELETE FROM {SCHEMA}.{table} WHERE years <> 'any'"))
        op.drop_constraint(pk, table, schema=SCHEMA, type_="primary")
        op.drop_column(table, "years", schema=SCHEMA)
        op.create_primary_key(pk, table, key, schema=SCHEMA)
    op.drop_column("job_posting_facts", "years_min", schema=SCHEMA)
