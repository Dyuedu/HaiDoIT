"""Fixture dùng chung cho test các bước ingest và lifecycle (Story 1.4)."""

from dataclasses import dataclass

import pytest
from sqlalchemy import Engine, text

from haido_core.config import RulesConfig, load_rules
from haido_core.db.engine import make_source_engine
from haido_core.db.scraper_source import ScraperPostgresReader
from haido_core.steps.aggregate import aggregate_snapshot
from haido_core.steps.ingest import ingest_snapshot
from haido_core.steps.lifecycle import lifecycle_snapshot
from haido_core.steps.publish import publish_snapshot

S = "2026-11-03"


@dataclass
class Env:
    write: Engine
    reader: ScraperPostgresReader
    rules: RulesConfig

    def ingest(self, day: str = S):
        return ingest_snapshot(day, reader=self.reader, engine=self.write, rules=self.rules)

    def lifecycle(self, day: str = S, rules: RulesConfig | None = None):
        return lifecycle_snapshot(day, engine=self.write, rules=rules or self.rules)

    def aggregate(self, day: str = S, rules: RulesConfig | None = None):
        return aggregate_snapshot(day, engine=self.write, rules=rules or self.rules)

    def publish(self, day: str = S, rules: RulesConfig | None = None):
        return publish_snapshot(day, engine=self.write, rules=rules or self.rules)

    def count(self, table: str) -> int:
        with self.write.connect() as conn:
            return conn.execute(text(f"SELECT count(*) FROM haido.{table}")).scalar_one()

    def counts(self) -> dict[str, int]:
        names = ("snapshots", "pipeline_runs", "job_postings", "job_posting_facts", "job_observations")
        return {n: self.count(n) for n in names}

    def query(self, sql: str, **params):
        with self.write.connect() as conn:
            return conn.execute(text(sql), params).all()


@pytest.fixture
def env(pg_engine: Engine, pg_url: str):
    source = make_source_engine(pg_url)
    yield Env(pg_engine, ScraperPostgresReader(source), load_rules())
    source.dispose()
