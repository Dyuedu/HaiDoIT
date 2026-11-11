"""Tỷ trọng thành phố theo cấp bậc lọc được của bản đồ (#163).

Revision ID: 0005_haido_city_share_level
Revises: 0004_haido_stat_sources
Create Date: 2026-11-11 00:00:00

`stat_city_shares` có thêm cột `seniority` trong khóa chính: `all` cho tỷ trọng của mọi cấp bậc, hoặc mã cấp
lọc (`entry`, `intern`, ..., `unknown`; xem `level_options` trong `config/rules.toml`). Hàng cũ là tỷ trọng
của mọi cấp bậc nên nhận `all`. `stat_cells` đã có cột `seniority` trong khóa từ 0003, không đổi.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_haido_city_share_level"
down_revision: str | Sequence[str] | None = "0004_haido_stat_sources"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"
TABLE = "stat_city_shares"
PK = "stat_city_shares_pkey"


def upgrade() -> None:
    # server_default chỉ để lấp hàng cũ; bỏ ngay sau đó để bước ghi buộc phải nêu cấp bậc.
    op.add_column(TABLE, sa.Column("seniority", sa.Text(), nullable=False, server_default="all"), schema=SCHEMA)
    op.alter_column(TABLE, "seniority", server_default=None, schema=SCHEMA)
    op.drop_constraint(PK, TABLE, schema=SCHEMA, type_="primary")
    op.create_primary_key(PK, TABLE, ["snapshot_id", "role", "seniority", "city"], schema=SCHEMA)


def downgrade() -> None:
    op.execute(sa.text(f"DELETE FROM {SCHEMA}.{TABLE} WHERE seniority <> 'all'"))
    # ô theo cấp (`stat_cells.seniority <> 'all'`) cũng do #163 thêm; bỏ cùng để bản cũ không đọc nhầm.
    op.execute(sa.text(f"DELETE FROM {SCHEMA}.stat_cells WHERE seniority <> 'all'"))
    op.drop_constraint(PK, TABLE, schema=SCHEMA, type_="primary")
    op.drop_column(TABLE, "seniority", schema=SCHEMA)
    op.create_primary_key(PK, TABLE, ["snapshot_id", "role", "city"], schema=SCHEMA)
