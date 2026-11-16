"""Tỷ lệ kỹ năng theo ô, dày (#101).

Revision ID: 0009_haido_skill_rates
Revises: 0008_haido_fact_city
Create Date: 2026-11-16 09:00:00

`stat_skill_rates`: mỗi (ô, kỹ năng) một hàng, kể cả tỷ lệ 0 (AD-5). Khóa ô là khóa chính của `stat_cells` và là khóa
ngoại tới nó, nên mỗi số gắn snapshot và ô thật. Nhóm core, common, rare không lưu: tính lúc đọc từ θ (FR-9, #102).
Hạ cấp bỏ bảng.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009_haido_skill_rates"
down_revision: str | Sequence[str] | None = "0008_haido_fact_city"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"
CELL = ["snapshot_id", "role", "branch", "seniority", "years", "scope"]


def upgrade() -> None:
    op.create_table(
        "stat_skill_rates",
        *(sa.Column(name, sa.Date() if name == "snapshot_id" else sa.Text(), nullable=False) for name in CELL),
        sa.Column("skill", sa.Text(), nullable=False),
        sa.Column("n_with", sa.Integer(), nullable=False),
        sa.Column("rate", sa.Float(precision=53), nullable=False),
        sa.Column("vocab_version", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(*CELL, "skill"),
        sa.ForeignKeyConstraint(CELL, [f"{SCHEMA}.stat_cells.{c}" for c in CELL], name="fk_stat_skill_rates_cell"),
        sa.CheckConstraint("n_with >= 0", name="ck_stat_skill_rates_n_with"),
        sa.CheckConstraint("rate >= 0 AND rate <= 1", name="ck_stat_skill_rates_rate"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("stat_skill_rates", schema=SCHEMA)
