"""Nguồn có tin được đếm của snapshot (#259).

Revision ID: 0004_haido_stat_sources
Revises: 0003_haido_city_share
Create Date: 2026-11-10 00:00:00

Một bảng dẫn xuất trong schema `haido`, do bước `aggregate` ghi cùng transaction với `stat_cells` và
`stat_city_shares`: mỗi hàng là một nguồn có ít nhất một tin được đếm trong cửa sổ 60 ngày của snapshot.
API đọc bảng này theo khóa để trả `meta.sources`, không đọc bảng tin (AD-5, AD-7).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_haido_stat_sources"
down_revision: str | Sequence[str] | None = "0003_haido_city_share"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"


def upgrade() -> None:
    op.create_table(
        "stat_sources",
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("snapshot_id", "source"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("stat_sources", schema=SCHEMA)
