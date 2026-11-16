"""Kiểm thử cổng FR-22: tính tất định của lộ trình học."""

import io
import json
import shutil
import sys
from pathlib import Path

import pytest

import tools.gates.check_gates as check_gates

# Mọi fixture "sổ hoãn còn hạn" dùng ngày rất xa, để test không đỏ theo lịch. Chỉ các test trên
# repo thật (`test_fr22_real_repo_*`) gắn với hạn 2026-12-13 và cố ý đỏ sau ngày đó (xem chú thích ở đó).
FUTURE = "2099-12-31"


def test_fr22_no_order_path_with_valid_ledger_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/22",
            "due": FUTURE
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.SKIP
    assert "deferred" in detail.lower() or FUTURE in detail


def test_fr22_no_order_path_with_expired_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/22",
            "due": "2020-01-01"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL
    assert any("quá hạn" in d.lower() or "expired" in d.lower() for d in [detail] + hits)


def test_fr22_no_order_path_with_invalid_issue_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "not-a-valid-url",
            "due": FUTURE
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL


def test_fr22_no_order_path_missing_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL


REAL_DOMAIN = Path(check_gates.__file__).resolve().parents[2] / "haido_core" / "domain"
ISSUE_139 = "https://github.com/Dyuedu/HaiDoIT/issues/139"
DUMMY_ECHO = """\
def order_path(requests):
    return requests
"""
DUMMY_GAPS_AS_IS = """

class PathOrderer:
    def order_path(self, requests):
        return tuple(requests.gaps)
"""


def _copy_domain(tmp_path: Path, path_order_source: str) -> None:
    """Dựng `haido_core/domain` tối thiểu: registry thật, kèm `path_order.py` do test chọn."""
    pkg = tmp_path / "haido_core"
    dom = pkg / "domain"
    dom.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (dom / "__init__.py").write_text("", encoding="utf-8")
    shutil.copy(REAL_DOMAIN / "registry.py", dom / "registry.py")
    (dom / "path_order.py").write_text(path_order_source, encoding="utf-8")


def _ledger(tmp_path: Path, **entries: dict) -> None:
    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "deferred.json").write_text(json.dumps(entries), encoding="utf-8")


def _signals(due: str = FUTURE) -> dict:
    return {"issue": ISSUE_139, "due": due}


def _real_source() -> str:
    return (REAL_DOMAIN / "path_order.py").read_text(encoding="utf-8")


def test_fr22_dummy_order_path_that_returns_its_input_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, DUMMY_ECHO)
    _ledger(tmp_path, **{"FR-22": _signals()})

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL
    assert hits


def test_fr22_order_path_that_follows_input_order_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    # Sửa bản thật để bỏ tầng khóa (chỉ giữ thứ tự gaps đầu vào): kết quả phụ thuộc thứ tự đầu vào.
    broken = _real_source() + DUMMY_GAPS_AS_IS
    _copy_domain(tmp_path, broken)
    _ledger(tmp_path, **{"FR-22": _signals()})

    status, _detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL
    assert hits


def test_fr22_real_implementation_copied_to_a_tmp_root_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, _real_source())
    _ledger(tmp_path, **{"FR-22": _signals()})

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.PASS, hits
    assert hits == []
    assert FUTURE in detail
    assert ISSUE_139 in detail


def test_fr22_gate_fails_once_the_signals_deferral_has_expired(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, _real_source())
    _ledger(tmp_path, **{"FR-22": _signals("2020-01-01")})

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL
    assert any("2020-01-01" in line for line in [detail] + hits)


def test_fr22_gate_fails_when_the_signals_deferral_is_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, _real_source())
    _ledger(tmp_path)

    status, _detail, _hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL


# Test dưới đây dùng repo thật và sổ hoãn thật. Nó CỐ Ý đỏ sau 2026-12-13 (hạn AC2 của #139):
# khi đó phải làm AC2 (mức khớp, tín hiệu, câu Insights), mở rộng cổng rồi bỏ mục FR-22.
def test_fr22_real_repo_passes_with_the_signals_deferral_in_the_detail():
    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.PASS, hits
    assert ISSUE_139 in detail
    assert "2026-12-13" in detail
    assert "still deferred: match level, signals, insight sentences" in detail
    assert "code not present yet" not in detail


def test_fr22_real_repo_ledger_only_defers_the_signals_part():
    ledger = json.loads((Path(check_gates.__file__).parent / "deferred.json").read_text(encoding="utf-8"))
    # Hạn 2026-11-22 của phần thứ tự đã qua mặt: mục chỉ còn giữ AC2, hạn 2026-12-13.
    assert ledger["FR-22"]["due"] == "2026-12-13"
    assert ledger["FR-22"]["issue"] == ISSUE_139


def test_fr22_ci_requires_the_gate():
    ci = (Path(check_gates.__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    line = next(row for row in ci.splitlines() if "check_gates.py --require" in row)
    assert "FR-22" in line.split()


# ---------------------------------------------------------------- AC2 phải hiện trong log CI


def _run_main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr(check_gates, "RESULTS", [])
    monkeypatch.setattr(check_gates, "GATES", [check_gates.gate_fr22_tat_dinh])
    monkeypatch.setattr(sys, "argv", ["check_gates.py", *argv])
    return check_gates.main()


def test_fr22_main_prints_the_signals_deferral_reminder_for_a_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, _real_source())
    _ledger(tmp_path, **{"FR-22": _signals()})

    assert _run_main(monkeypatch, "--require", "FR-22") == 0
    out = capsys.readouterr().out
    assert "FR-22" in out
    assert "PASS" in out
    assert "still deferred: match level, signals, insight sentences" in out
    assert FUTURE in out
    assert ISSUE_139 in out


def test_fr22_main_does_not_print_detail_for_a_pass_without_a_reminder(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    quiet = check_gates.gate("X-1", "quiet")(lambda: (check_gates.PASS, "12 files scanned", []))
    monkeypatch.setattr(check_gates, "RESULTS", [])
    monkeypatch.setattr(check_gates, "GATES", [quiet])
    monkeypatch.setattr(sys, "argv", ["check_gates.py"])
    assert check_gates.main() == 0
    assert "12 files scanned" not in capsys.readouterr().out


def test_fr22_main_survives_vietnamese_in_a_failing_detail_on_a_cp1252_pipe(monkeypatch: pytest.MonkeyPatch):
    raw = io.BytesIO()
    pipe = io.TextIOWrapper(raw, encoding="cp1252", write_through=True)
    failing = check_gates.gate("X-2", "viet")(lambda: (check_gates.FAIL, "d", ["Khoảng trống không hợp lệ"]))
    monkeypatch.setattr(check_gates, "RESULTS", [])
    monkeypatch.setattr(check_gates, "GATES", [failing])
    monkeypatch.setattr(sys, "argv", ["check_gates.py"])
    monkeypatch.setattr(sys, "stdout", pipe)
    assert check_gates.main() == 1
    assert b"Kho" in raw.getvalue()


# ---------------------------------------------------------------- chính các phép kiểm của cổng
# Mỗi bản giả đúng hình dạng (class PathOrderer, lô trả tuple) nên probe không crash: cổng phải FAIL
# vì chính phép kiểm tương ứng. Test khẳng định câu hit cụ thể để xóa một phép kiểm là test đỏ.

_CLOSURE = """
from haido_core.domain.registry import as_batch


def _ancestors(r):
    before = {}
    for e in r.edges:
        before.setdefault(e.after, set()).add(e.before)
    seen, stack = set(), list(r.gaps)
    while stack:
        n = stack.pop()
        if n not in seen:
            seen.add(n)
            stack.extend(before.get(n, ()))
    return before, seen


class PathOrderer:
    def order_path(self, requests):
        batch = as_batch(requests)
        if batch is None:
            return self._one(requests)
        return tuple(self._one(x) for x in batch)
"""

# (a) Tất định, đúng hình dạng, nhưng SAI thứ tự: gaps cộng tổ tiên xếp A-Z.
DUMMY_ALPHABETICAL = _CLOSURE + """
    def _one(self, r):
        return tuple(sorted(_ancestors(r)[1]))
"""

# (b) Đúng thứ tự trên đầu vào gốc (hòa nhau thì theo vị trí trong `skills`, vốn đã A-Z), nhưng
# phụ thuộc thứ tự đầu vào: xáo `skills` là ra thứ tự khác.
DUMMY_INPUT_ORDER = _CLOSURE + """
    def _one(self, r):
        before, seen = _ancestors(r)
        by_id = {s.skill_id: s for s in r.skills}
        rank = {"core": 0, "common": 1, "rare": 2}
        waiting = [s.skill_id for s in r.skills if s.skill_id in seen]
        done, out = set(), []
        while waiting:
            ready = [n for n in waiting if before.get(n, set()) <= done]
            best = min(ready, key=lambda n: (by_id[n].stage, rank[by_id[n].band.value], -by_id[n].rate))
            out.append(best)
            done.add(best)
            waiting.remove(best)
        return tuple(out)
"""

# (c) Bản thật cho một yêu cầu, nhưng với lô thì chỉ trả phần tử đầu.
DUMMY_BAD_BATCH_SUFFIX = """

_real_order_path = PathOrderer.order_path


def _order_path(self, requests):
    if isinstance(requests, list | tuple):
        return _real_order_path(self, requests)[:1]
    return _real_order_path(self, requests)


PathOrderer.order_path = _order_path
"""

# (d) Thứ tự theo `hash(str)`: không phụ thuộc thứ tự đầu vào, nhưng đổi theo PYTHONHASHSEED.
DUMMY_HASH_SEED = _CLOSURE + """
    def _one(self, r):
        return tuple(sorted(_ancestors(r)[1], key=hash))
"""

# (e) Ném ValueError có tiếng Việt: probe phải báo được, không crash lúc đọc stderr.
DUMMY_VIETNAMESE_CRASH = """
class PathOrderer:
    def order_path(self, requests):
        raise ValueError("Khoảng trống é à")
"""


def _gate_on(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    _copy_domain(tmp_path, source)
    _ledger(tmp_path, **{"FR-22": _signals()})
    return check_gates.gate_fr22_tat_dinh()


def _wanted(hits: list[str], *fragments: str) -> bool:
    return any(all(f in hit for f in fragments) for hit in hits)


def test_fr22_gate_fails_on_a_well_formed_but_wrong_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    status, _detail, hits = _gate_on(tmp_path, monkeypatch, DUMMY_ALPHABETICAL)
    assert status == check_gates.FAIL
    assert _wanted(hits, "expected"), hits
    assert not _wanted(hits, "crashed"), hits
    assert not _wanted(hits, "shuffled"), hits
    assert not _wanted(hits, "differs between"), hits


def test_fr22_gate_fails_when_the_result_depends_on_input_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    status, _detail, hits = _gate_on(tmp_path, monkeypatch, DUMMY_INPUT_ORDER)
    assert status == check_gates.FAIL
    assert _wanted(hits, "shuffled requests gave a different order"), hits
    assert not _wanted(hits, "expected"), hits  # đúng trên đầu vào gốc: chỉ phép kiểm xáo bắt được
    assert not _wanted(hits, "crashed"), hits


def test_fr22_gate_fails_when_a_batch_gives_a_different_shape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    status, _detail, hits = _gate_on(tmp_path, monkeypatch, _real_source() + DUMMY_BAD_BATCH_SUFFIX)
    assert status == check_gates.FAIL
    assert _wanted(hits, "batch of two requests"), hits
    assert not _wanted(hits, "expected"), hits
    assert not _wanted(hits, "crashed"), hits


def test_fr22_gate_fails_when_the_result_depends_on_the_hash_seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    status, _detail, hits = _gate_on(tmp_path, monkeypatch, DUMMY_HASH_SEED)
    assert status == check_gates.FAIL
    assert _wanted(hits, "differs between PYTHONHASHSEED=0 and PYTHONHASHSEED=1"), hits
    assert not _wanted(hits, "crashed"), hits


def test_fr22_gate_reports_a_vietnamese_crash_message_without_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # Windows: tiến trình con không ở chế độ UTF-8, stderr là cp1252. Bỏ các biến này để tái hiện.
    monkeypatch.delenv("PYTHONUTF8", raising=False)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    status, detail, hits = _gate_on(tmp_path, monkeypatch, DUMMY_VIETNAMESE_CRASH)
    assert status == check_gates.FAIL
    assert "gate crashed" not in detail
    assert _wanted(hits, "crashed", "ValueError", "Khoảng trống"), hits


def test_fr22_probe_runs_the_configured_number_of_shuffles():
    assert check_gates.FR22_SHUFFLES >= 20
    result, problem = check_gates._fr22_probe("0")
    assert result is not None, problem
    # Một biến thể đảo ngược cộng FR22_SHUFFLES biến thể xáo.
    assert len(result["shuffled"]) == check_gates.FR22_SHUFFLES + 1


def test_fr22_gate_compares_two_different_hash_seeds(monkeypatch: pytest.MonkeyPatch):
    seeds: list[str] = []
    real = check_gates._fr22_probe

    def spy(seed: str):
        seeds.append(seed)
        return real(seed)

    monkeypatch.setattr(check_gates, "_fr22_probe", spy)
    check_gates.gate_fr22_tat_dinh()
    assert len(set(seeds)) == 2
