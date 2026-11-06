"""Schema haido: snapshot, lượt chạy, tin, dữ kiện tin, quan sát, vòng đời (Story 1.4).

Revision ID: 0002_haido_snapshot
Revises: 0001_initial
Create Date: 2026-11-06 00:00:00

Bảng nằm trong schema riêng `haido`, không đụng bảng của scraper ở `public`.
`job_observations` và `job_posting_facts` chỉ thêm: trigger chặn UPDATE, DELETE, TRUNCATE.
Không có cột văn bản JD, liên hệ người đăng hay mô tả (DoD dòng 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_haido_snapshot"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "haido"
APPEND_ONLY = ("job_observations", "job_posting_facts")


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA {SCHEMA}")

    op.create_table(
        "snapshots",
        sa.Column("snapshot_id", sa.Date(), primary_key=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sources_failed", sa.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'::text[]")),
        sa.CheckConstraint("status IN ('open', 'published', 'partial')", name="ck_snapshots_status"),
        schema=SCHEMA,
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("seen_count", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.CheckConstraint("mode IN ('auto', 'manual')", name="ck_pipeline_runs_mode"),
        sa.UniqueConstraint("snapshot_id", "source", name="uq_pipeline_runs_snapshot_source"),
        schema=SCHEMA,
    )

    op.create_table(
        "job_postings",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.UniqueConstraint("source", "source_url", name="uq_job_postings_source_url"),
        schema=SCHEMA,
    )

    op.create_table(
        "job_posting_facts",
        sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey(f"{SCHEMA}.job_postings.id"), nullable=False),
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("company", sa.Text(), nullable=True),
        sa.Column("location_text", sa.Text(), nullable=True),
        sa.Column("experience_level", sa.Text(), nullable=True),
        sa.Column("job_level", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("posting_id", "snapshot_id"),
        schema=SCHEMA,
    )

    op.create_table(
        "job_observations",
        sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey(f"{SCHEMA}.job_postings.id"), nullable=False),
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column(
            "pipeline_run_id", sa.BigInteger(), sa.ForeignKey(f"{SCHEMA}.pipeline_runs.id"), nullable=False
        ),
        sa.PrimaryKeyConstraint("posting_id", "snapshot_id"),
        schema=SCHEMA,
    )
    op.create_index("ix_job_observations_snapshot", "job_observations", ["snapshot_id"], schema=SCHEMA)

    op.create_table(
        "stat_job_lifecycle",
        sa.Column("snapshot_id", sa.Date(), sa.ForeignKey(f"{SCHEMA}.snapshots.snapshot_id"), nullable=False),
        sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey(f"{SCHEMA}.job_postings.id"), nullable=False),
        sa.Column("times_seen", sa.Integer(), nullable=False),
        sa.Column("first_seen", sa.Date(), nullable=False),
        sa.Column("last_seen", sa.Date(), nullable=False),
        sa.Column("repost_count", sa.Integer(), nullable=False),
        sa.Column("absent", sa.Boolean(), nullable=False),
        sa.Column("in_window", sa.Boolean(), nullable=False),
        sa.Column("config_version", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("snapshot_id", "posting_id"),
        schema=SCHEMA,
    )

    op.execute(
        f"""
        CREATE FUNCTION {SCHEMA}.forbid_modify() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Bảng %.% chỉ được thêm hàng: không UPDATE, DELETE hay TRUNCATE.',
                TG_TABLE_SCHEMA, TG_TABLE_NAME
                USING ERRCODE = 'restrict_violation';
        END;
        $$
        """
    )
    for table in APPEND_ONLY:
        op.execute(
            f"CREATE TRIGGER trg_{table}_append_only BEFORE UPDATE OR DELETE ON {SCHEMA}.{table} "
            f"FOR EACH ROW EXECUTE FUNCTION {SCHEMA}.forbid_modify()"
        )
        op.execute(
            f"CREATE TRIGGER trg_{table}_no_truncate BEFORE TRUNCATE ON {SCHEMA}.{table} "
            f"FOR EACH STATEMENT EXECUTE FUNCTION {SCHEMA}.forbid_modify()"
        )


def downgrade() -> None:
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
