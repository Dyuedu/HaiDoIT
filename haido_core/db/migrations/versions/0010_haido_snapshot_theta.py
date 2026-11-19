"""Phiên bản θ của snapshot (#102).

Revision ID: 0010_haido_snapshot_theta
Revises: 0009_haido_skill_rates
Create Date: 2026-11-19 09:00:00

`snapshots.theta_version` (text, nullable): phiên bản θ trong `config/theta.toml` mà bước `aggregate` đã dùng cho snapshot.
API nhóm kỹ năng của snapshot bằng θ của phiên bản này, không bằng θ hiện hành, nên đổi θ sau này không làm snapshot cũ
đổi nhóm. NULL ở snapshot tính trước khi đóng băng: đọc là phiên bản đầu của sổ đăng ký (`theta-1`, giá trị khi đó).
Không điền lại hàng cũ để migration không phụ thuộc file cấu hình. Hạ cấp bỏ cột.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0010_haido_snapshot_theta"
down_revision: str | Sequence[str] | None = "0009_haido_skill_rates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"


def upgrade() -> None:
    op.add_column("snapshots", sa.Column("theta_version", sa.Text()), schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("snapshots", "theta_version", schema=SCHEMA)
