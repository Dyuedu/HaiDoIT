"""Bảng của schema `haido` (Story 1.4, #93). Phải khớp migration `0002_haido_snapshot`, `0003_haido_city_share`, `0004_haido_stat_sources`, `0005_haido_city_share_level` và `0006_haido_years_filter`.

Chỉ `haido_core/steps/` ghi các bảng này. `haido_api` không đọc `job_*` (AD-5, AD-7).
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

SCHEMA = "haido"

metadata = sa.MetaData(schema=SCHEMA)

snapshots = sa.Table(
    "snapshots",
    metadata,
    sa.Column("snapshot_id", sa.Date(), primary_key=True),
    sa.Column("status", sa.Text(), nullable=False, server_default="open"),
    sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.Column("closed_at", sa.DateTime(timezone=True)),
    sa.Column("sources_failed", sa.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'::text[]")),
)

pipeline_runs = sa.Table(
    "pipeline_runs",
    metadata,
    sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), nullable=False),
    sa.Column("source", sa.Text(), nullable=False),
    sa.Column("mode", sa.Text(), nullable=False),
    sa.Column("success", sa.Boolean(), nullable=False),
    sa.Column("seen_count", sa.Integer(), nullable=False),
    sa.Column("error", sa.Text()),
)

job_postings = sa.Table(
    "job_postings",
    metadata,
    sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
    sa.Column("source", sa.Text(), nullable=False),
    sa.Column("source_url", sa.Text(), nullable=False),
)

job_posting_facts = sa.Table(
    "job_posting_facts",
    metadata,
    sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey("haido.job_postings.id"), primary_key=True),
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("title", sa.Text()),
    sa.Column("company", sa.Text()),
    sa.Column("location_text", sa.Text()),
    sa.Column("experience_level", sa.Text()),
    sa.Column("job_level", sa.Text()),
    sa.Column("years_min", sa.Float(precision=53)),
)

job_observations = sa.Table(
    "job_observations",
    metadata,
    sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey("haido.job_postings.id"), primary_key=True),
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("pipeline_run_id", sa.BigInteger(), sa.ForeignKey("haido.pipeline_runs.id"), nullable=False),
)

stat_job_lifecycle = sa.Table(
    "stat_job_lifecycle",
    metadata,
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("posting_id", sa.BigInteger(), sa.ForeignKey("haido.job_postings.id"), primary_key=True),
    sa.Column("times_seen", sa.Integer(), nullable=False),
    sa.Column("first_seen", sa.Date(), nullable=False),
    sa.Column("last_seen", sa.Date(), nullable=False),
    sa.Column("repost_count", sa.Integer(), nullable=False),
    sa.Column("absent", sa.Boolean(), nullable=False),
    sa.Column("in_window", sa.Boolean(), nullable=False),
    sa.Column("config_version", sa.Text(), nullable=False),
)

stat_cells = sa.Table(
    "stat_cells",
    metadata,
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("role", sa.Text(), primary_key=True),
    sa.Column("branch", sa.Text(), primary_key=True),
    sa.Column("seniority", sa.Text(), primary_key=True),
    sa.Column("years", sa.Text(), primary_key=True),
    sa.Column("scope", sa.Text(), primary_key=True),
    sa.Column("n", sa.Integer(), nullable=False),
    sa.Column("seniority_mix", JSONB(), nullable=False),
    sa.Column("years_unstated", sa.Integer(), nullable=False),
    sa.Column("config_version", sa.Text(), nullable=False),
)

stat_city_shares = sa.Table(
    "stat_city_shares",
    metadata,
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("role", sa.Text(), primary_key=True),
    sa.Column("seniority", sa.Text(), primary_key=True),
    sa.Column("years", sa.Text(), primary_key=True),
    sa.Column("city", sa.Text(), primary_key=True),
    sa.Column("share", sa.Float(precision=53), nullable=False),
)

stat_sources = sa.Table(
    "stat_sources",
    metadata,
    sa.Column("snapshot_id", sa.Date(), sa.ForeignKey("haido.snapshots.snapshot_id"), primary_key=True),
    sa.Column("source", sa.Text(), primary_key=True),
)
