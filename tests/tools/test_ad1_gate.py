"""Kiểm thử cổng AD-1: hướng phụ thuộc không đảo."""

import json
from pathlib import Path

import pytest

import tools.gates.check_gates as check_gates


@pytest.mark.parametrize("scheme", ["postgres://", "postgresql://", "postgresql+psycopg://"])
def test_ad1_web_postgres_connection_string_variants(scheme: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    web_dir = tmp_path / "web" / "app"
    web_dir.mkdir(parents=True)
    page_file = web_dir / "page.tsx"
    page_file.write_text(f'const db = "{scheme}user:pass@localhost:5432/haido";', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.FAIL
    assert any("page.tsx:1" in h and "web contains postgres connection string" in h for h in hits)


def test_ad1_credential_not_printed_in_hit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    web_dir = tmp_path / "web" / "app"
    web_dir.mkdir(parents=True)
    page_file = web_dir / "page.tsx"
    page_file.write_text('const db = "postgresql+psycopg://secret_user:SECRET_PASS_CANARY@localhost/db";', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.FAIL
    assert not any("SECRET_PASS_CANARY" in h for h in hits)
    assert any("page.tsx:1" in h for h in hits)


@pytest.mark.parametrize("dep_field", ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"])
@pytest.mark.parametrize("pkg_name", ["pg", "postgres"])
def test_ad1_web_driver_dependency_variants(dep_field: str, pkg_name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    web_dir = tmp_path / "web"
    web_dir.mkdir(parents=True)
    pkg_json = web_dir / "package.json"
    data = {"name": "web", dep_field: {pkg_name: "^1.0.0"}}
    pkg_json.write_text(json.dumps(data), encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.FAIL
    assert any(pkg_name in h and "package.json" in h for h in hits)


@pytest.mark.parametrize("import_stmt", [
    "from haido_core import db",
    "from .. import db",
    "from ..db import x",
    "from ...db import x",
    "from haido_core import steps",
    "from .. import steps",
    "from ..steps import x",
    "from ...steps import x",
    "import psycopg",
    "import alembic",
])
def test_ad1_domain_reverse_import_variants(import_stmt: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    domain_dir = tmp_path / "haido_core" / "domain"
    domain_dir.mkdir(parents=True)
    (domain_dir / "bad_mod.py").write_text(f"{import_stmt}\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.FAIL
    assert len(hits) == 1


def test_ad1_unparsable_package_json_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    web_dir = tmp_path / "web"
    web_dir.mkdir(parents=True)
    pkg_json = web_dir / "package.json"
    pkg_json.write_text("{ invalid json: not finished", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.FAIL
    assert any("package.json" in h and "unparsable" in h for h in hits)


def test_ad1_clean_tree_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    domain_dir = tmp_path / "haido_core" / "domain"
    domain_dir.mkdir(parents=True)
    (domain_dir / "pure.py").write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")

    web_dir = tmp_path / "web"
    web_dir.mkdir(parents=True)
    (web_dir / "package.json").write_text('{"name": "web", "dependencies": {"next": "16.4.4"}}', encoding="utf-8")
    (web_dir / "page.tsx").write_text("export default function Page() { return null; }", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad1_huong_phu_thuoc()
    assert status == check_gates.PASS
    assert hits == []


def test_ad25_zero_revisions_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    vers_dir = tmp_path / "haido_core" / "db" / "migrations" / "versions"
    vers_dir.mkdir(parents=True)
    # Thư mục versions rỗng (không có file revision nào)
    status, _detail, _heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.FAIL
