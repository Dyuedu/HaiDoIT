"""Kiểm thử cổng FR-25/31/47: câu chữ bị cấm."""

from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates

BANNED_PHRASES = [
    "đừng học",
    "bỏ qua một kỹ năng",
    "lừa đảo",
    "tin giả",
    "tin ma",
    "tuân thủ đầy đủ điều khoản của mọi nguồn",
    "mọi dữ liệu đều đã được cấp phép",
]


@pytest.mark.parametrize("phrase", BANNED_PHRASES)
def test_fr25_fr31_fr47_banned_phrases_in_web_app_fails(phrase: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    app_dir = tmp_path / "web" / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "page.tsx").write_text(f"export default function Page() {{ return <div>{phrase}</div>; }}", encoding="utf-8")

    status, _detail, hits = check_gates.gate_fr_cau_chu_bi_cam()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "web/app/page.tsx:1" in hits[0]


@pytest.mark.parametrize("phrase", BANNED_PHRASES)
def test_fr25_fr31_fr47_banned_phrases_in_tests_ignored(phrase: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    # File trong web/tests/
    web_tests = tmp_path / "web" / "tests"
    web_tests.mkdir(parents=True)
    (web_tests / "sample.test.tsx").write_text(f"// Test checking: {phrase}\n", encoding="utf-8")

    # File test .test.ts và .test.tsx ngoài tests/
    web_app = tmp_path / "web" / "app"
    web_app.mkdir(parents=True)
    (web_app / "page.test.tsx").write_text(f"// Checking {phrase}\n", encoding="utf-8")
    (web_app / "helper.test.ts").write_text(f"// Checking {phrase}\n", encoding="utf-8")

    # File trong tests/ ở gốc repo
    root_tests = tmp_path / "tests" / "unit"
    root_tests.mkdir(parents=True)
    (root_tests / "test_example.py").write_text(f'CANARY = "{phrase}"\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_fr_cau_chu_bi_cam()
    assert status == check_gates.PASS
    assert hits == []


def test_fr25_fr31_fr47_ignored_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    node_modules = tmp_path / "web" / "node_modules" / "some_pkg"
    node_modules.mkdir(parents=True)
    (node_modules / "index.js").write_text('console.log("lừa đảo");', encoding="utf-8")

    next_dir = tmp_path / "web" / ".next" / "static"
    next_dir.mkdir(parents=True)
    (next_dir / "bundle.js").write_text('console.log("tin giả");', encoding="utf-8")

    status, _detail, hits = check_gates.gate_fr_cau_chu_bi_cam()
    assert status == check_gates.PASS
    assert hits == []


def test_fr25_fr31_fr47_real_repo_passes():
    status, _detail, hits = check_gates.gate_fr_cau_chu_bi_cam()
    assert status == check_gates.PASS
    assert hits == []
