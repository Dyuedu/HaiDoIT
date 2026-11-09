"""Ô thống kê và tỷ trọng thành phố của snapshot (#93).

Revision ID: 0003_haido_city_share
Revises: 0002_haido_snapshot
Create Date: 2026-11-09 00:00:00

Hai bảng dẫn xuất trong schema `haido`, do bước `aggregate` ghi một lần cho mỗi snapshot `open`:

- `stat_cells`: số tin và pha cấp bậc của từng ô. `branch` và `seniority` là `all` cho tới khi có
  nhánh và cấp bậc riêng; `scope` là mã thành phố hoặc `vn`.
- `stat_city_shares`: tỷ trọng của từng thành phố trong số tin toàn quốc của một vai trò.

API đọc hai bảng này theo khóa, không cộng lại từ bảng tin (AD-5, AD-7).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_haido_city_share"
down_revision: str | Sequence[str] | None = "0002_haido_snapshot"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"


def upgrade() -> None:
    op.create_table(
        "stat_cells",
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("branch", sa.Text(), nullable=False),
        sa.Column("seniority", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("n", sa.Integer(), nullable=False),
        sa.Column("seniority_mix", postgresql.JSONB(), nullable=False),
        sa.Column("config_version", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("snapshot_id", "role", "branch", "seniority", "scope"),
        sa.CheckConstraint("n >= 0", name="ck_stat_cells_n"),
        schema=SCHEMA,
    )
    op.create_table(
        "stat_city_shares",
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("share", sa.Float(precision=53), nullable=False),
        sa.PrimaryKeyConstraint("snapshot_id", "role", "city"),
        sa.CheckConstraint("share >= 0 AND share <= 1", name="ck_stat_city_shares_share"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("stat_city_shares", schema=SCHEMA)
    op.drop_table("stat_cells", schema=SCHEMA)
