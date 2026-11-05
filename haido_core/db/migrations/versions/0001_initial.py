"""Initial empty migration

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-05 00:00:00

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Migration đầu tiên rỗng (AD-25, không tạo bảng nghiệp vụ)."""


def downgrade() -> None:
    """Downgrade về base."""
