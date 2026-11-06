#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Chín cổng kiến trúc của AD-24 — chặn merge.

Mỗi cổng là một hàm có tên chứa mã AD hoặc FR, đúng yêu cầu của AD-24.

Ba trạng thái:
  PASS      cổng chạy và không thấy vi phạm
  BO QUA   phần mã mà cổng canh chưa tồn tại — cổng tự bật khi mã xuất hiện
  FAIL     có vi phạm, thoát mã 1

Chạy tay:   python tools/gates/check_gates.py
Nghiêm ngặt: python tools/gates/check_gates.py --require AD-1 AD-2 AD-25
             (những cổng nêu tên mà còn BO QUA cũng tính là FAIL)
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PASS, SKIP, FAIL = "PASS", "SKIP", "FAIL"
RESULTS: list[tuple[str, str, str, list[str]]] = []


def gate(code: str, name: str):
    def deco(fn):
        def run():
            try:
                status, detail, hits = fn()
            except Exception as exc:  # cổng hỏng thì báo, không nuốt
                status, detail, hits = FAIL, "gate crashed: %r" % (exc,), []
            RESULTS.append((code, name, status, hits if hits else [detail]))
            return status, detail, hits
        run.__name__ = fn.__name__
        return run
    return deco


def py_files(*dirs: str) -> list[Path]:
    out: list[Path] = []
    for d in dirs:
        p = ROOT / d
        if p.is_dir():
            out += [f for f in p.rglob("*.py") if "__pycache__" not in f.parts]
    return out


def any_dir(*dirs: str) -> bool:
    return any((ROOT / d).is_dir() for d in dirs)


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def scan(files, pattern, flags=0):
    rx = re.compile(pattern, flags)
    hits = []
    for f in files:
        for i, line in enumerate(read(f).splitlines(), 1):
            if rx.search(line):
                hits.append("%s:%d: %s" % (f.relative_to(ROOT).as_posix(), i, line.strip()[:90]))
    return hits


# ---------------------------------------------------------------- AD-1
@gate("AD-1", "Dependency direction not inverted")
def gate_ad1_huong_phu_thuoc():
    checks = [
        ("haido_core/domain", r"^\s*(from|import)\s+(sqlalchemy|dagster|fastapi|psycopg|alembic)\b",
         "domain pulls in infrastructure"),
        ("haido_core/domain", r"^\s*(from\s+haido_core\.(db|steps)\b|from\s+haido_core\s+import\s+.*\b(db|steps)\b|import\s+haido_core\.(db|steps)\b|from\s+\.{2,}\s*import\s+.*\b(db|steps)\b|from\s+\.{2,}(db|steps)\b)",
         "domain imports outer core (db/steps)"),
        ("haido_core/steps", r"^\s*(from|import)\s+dagster\b", "steps imports Dagster"),
        ("haido_core", r"^\s*(from|import)\s+(haido_api|haido_pipeline)\b", "core imports api or pipeline"),
        ("haido_pipeline", r"^\s*(from|import)\s+haido_api\b", "pipeline imports api"),
        ("haido_api", r"^\s*(from|import)\s+(dagster|haido_pipeline)\b", "api imports pipeline"),
    ]
    web_dir = ROOT / "web"
    web_present = web_dir.is_dir()
    present = [d for d, _, _ in checks if (ROOT / d).is_dir()]
    if not present and not web_present:
        return SKIP, "haido_core/, haido_api/, haido_pipeline/, and web/ not present yet", []
    hits = []
    for d, pat, why in checks:
        for h in scan(py_files(d), pat, re.M):
            hits.append("%s — %s" % (why, h))

    # Kiểm tra web/ không có chuỗi kết nối Postgres
    if web_present:
        web_files = [
            f for f in web_dir.rglob("*")
            if f.is_file() and "node_modules" not in f.parts and ".next" not in f.parts
        ]
        pg_conn_rx = re.compile(r"postgres(ql(\+psycopg)?)?://", re.I)
        for f in web_files:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(txt.splitlines(), 1):
                    if pg_conn_rx.search(line):
                        hits.append("web contains postgres connection string — %s:%d" % (
                            f.relative_to(ROOT).as_posix(), i
                        ))
            except Exception:
                hits.append("unreadable file in web/ — %s" % f.relative_to(ROOT).as_posix())

        # Kiểm tra web/package.json không có driver pg / postgres
        pkg_json = web_dir / "package.json"
        if pkg_json.is_file():
            try:
                import json
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    hits.append("web/package.json is unparsable JSON (not an object) — %s" % (
                        pkg_json.relative_to(ROOT).as_posix()
                    ))
                else:
                    deps = {}
                    deps.update(data.get("dependencies", {}))
                    deps.update(data.get("devDependencies", {}))
                    deps.update(data.get("peerDependencies", {}))
                    deps.update(data.get("optionalDependencies", {}))
                    for driver in ("pg", "postgres"):
                        if driver in deps:
                            hits.append("web/package.json has postgres driver dependency: %s — %s" % (
                                driver, pkg_json.relative_to(ROOT).as_posix()
                            ))
            except Exception as exc:
                hits.append("web/package.json is unparsable JSON: %s — %s" % (
                    exc, pkg_json.relative_to(ROOT).as_posix()
                ))

    return (FAIL if hits else PASS), "%d directories watched%s" % (
        len(present), " (including web/)" if web_present else ""
    ), hits


# ---------------------------------------------------------------- AD-2
# Tên hàm là hợp đồng SPEC-REG-03. Đổi tên thì sửa registry và cổng trong cùng PR.
AD2_FUNCTIONS = (
    "map_mentions",
    "select_cell",
    "population",
    "group_skills",
    "percentiles",
    "classify",
    "match_postings",
    "order_path",
)
AD2_KEYWORDS = (
    "mapping",
    "chọn ô",
    "dân số",
    "nhóm kỹ năng",
    "phân vị",
    "phân loại",
    "so khớp",
    "xếp thứ tự",
)
_AD2_SKIP_DIRS = frozenset({
    "tests",
    "tools",
    ".claude",
    "_bmad",
    "_bmad-output",
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
})


def _ad2_is_protocol(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Protocol":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "Protocol":
            return True
    return False


def ad2_duplicate_hits(root: Path) -> list[str]:
    """Chỗ chữ ký thừa, chữ ký thiếu, hoặc thân hàm thứ hai. Nhận root để test."""
    protocols: dict[str, list[str]] = {name: [] for name in AD2_FUNCTIONS}
    concretes: dict[str, list[str]] = {name: [] for name in AD2_FUNCTIONS}
    hits: list[str] = []
    for path in root.rglob("*.py"):
        if any(part in _AD2_SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(read(path), filename=rel)
        except SyntaxError as exc:
            hits.append("%s: không parse được (%s)" % (rel, exc.msg))
            continue
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if node.name not in protocols:
                continue
            parent = parents.get(node)
            kind = "concrete"
            if isinstance(parent, ast.ClassDef) and _ad2_is_protocol(parent):
                kind = "protocol"
            where = "%s:%d: %s %s" % (rel, node.lineno, kind, node.name)
            if kind == "protocol" and rel.startswith("haido_core/domain/"):
                protocols[node.name].append(where)
            else:
                concretes[node.name].append(where)
    domain = "haido_core/domain/"
    for name in AD2_FUNCTIONS:
        signed = protocols[name]
        if len(signed) != 1:
            hits.append("%s: cần đúng một Protocol trong domain/, thấy %d" % (name, len(signed)))
        outside = [item for item in concretes[name] if not item.startswith(domain)]
        inside = [item for item in concretes[name] if item.startswith(domain)]
        hits.extend(outside)
        if len(inside) > 1:
            hits.append("%s: hơn một thân hàm trong domain/" % name)
            hits.extend(inside)
    return hits


def ad2_status(root: Path) -> tuple[str, str, list[str]]:
    """PASS / SKIP / FAIL của AD-2 trên một cây thư mục."""
    reg = root / "haido_core" / "domain" / "REGISTRY.md"
    if not reg.exists():
        return SKIP, "haido_core/domain/REGISTRY.md not present yet", []
    txt = read(reg)
    missing = [n for n in AD2_KEYWORDS if n.lower() not in txt.lower()]
    if missing:
        return FAIL, "REGISTRY.md is missing operations", ["missing: " + ", ".join(missing)]
    hits = ad2_duplicate_hits(root)
    if hits:
        return FAIL, "registry is not closed", hits
    return PASS, "all eight operations declared", []


@gate("AD-2", "Registry closed over eight operations")
def gate_ad2_registry_dong():
    return ad2_status(ROOT)


# ---------------------------------------------------------------- AD-7
@gate("AD-7", "API must not aggregate over job_* tables")
def gate_ad7_khong_tong_hop_tren_job():
    if not (ROOT / "haido_api").is_dir():
        return SKIP, "haido_api/ not present yet", []
    hits = scan(py_files("haido_api"), r"\bjob_(postings|observations)\b")
    return (FAIL if hits else PASS), "scanned haido_api/", hits


# ---------------------------------------------------------------- AD-17
@gate("AD-17", "Envelope meta shape")
def gate_ad17_hinh_dang_meta():
    dom = ROOT / "haido_core" / "domain"
    if not dom.is_dir():
        return SKIP, "haido_core/domain/ not present yet", []
    need = ["snapshot_date", "snapshot_status", "sources", "sources_failed",
            "thresholds", "coverage_notes", "n_by_measure", "insufficient_by_measure"]
    blob = "\n".join(read(f) for f in py_files("haido_core/domain"))
    if "class Envelope" not in blob and "Envelope" not in blob:
        return FAIL, "no Envelope model found in domain/", []
    missing = [n for n in need if n not in blob]
    return (FAIL if missing else PASS), "Envelope model", (["missing fields: " + ", ".join(missing)] if missing else [])


# ---------------------------------------------------------------- AD-23
@gate("AD-23", "localStorage uses a closed key list")
def gate_ad23_khoa_dong():
    web = ROOT / "web"
    if not web.is_dir():
        return SKIP, "web/ not present yet", []
    files = [f for f in web.rglob("*.ts") if "node_modules" not in f.parts]
    files += [f for f in web.rglob("*.tsx") if "node_modules" not in f.parts]
    allow = re.compile(r"storage|haido-keys", re.I)
    hits = [h for h in scan(files, r"localStorage\.(get|set|remove)Item")
            if not allow.search(h.split(":")[0])]
    return (FAIL if hits else PASS), "localStorage calls outside the closed-key module", hits


# ---------------------------------------------------------------- FR-25/31/47
@gate("FR-25/31/47", "Banned wording")
def gate_fr_cau_chu_bi_cam():
    targets = [d for d in ("web", "haido_core", "haido_api") if (ROOT / d).is_dir()]
    if not targets:
        return SKIP, "product source not present yet", []
    banned = [
        r"bạn nên (ứng tuyển|nộp)", r"công ty (này )?(lừa đảo|ma)", r"tin (này )?là lừa đảo",
        r"chắc chắn (sẽ |)(đậu|trúng tuyển)", r"cam kết việc làm", r"lương (chuẩn|chính xác) là",
    ]
    files = []
    for d in targets:
        files += [f for f in (ROOT / d).rglob("*")
                  if f.is_file() and f.suffix in {".py", ".ts", ".tsx", ".md", ".json"}
                  and "node_modules" not in f.parts and "__pycache__" not in f.parts]
    hits = []
    for pat in banned:
        hits += scan(files, pat, re.I)
    return (FAIL if hits else PASS), "%d files scanned" % len(files), hits


# ---------------------------------------------------------------- FR-24
@gate("FR-24", "Blurbs contain no numbers")
def gate_fr24_loi_dan_khong_so():
    blurbs = ROOT / "haido_core" / "vocab" / "blurbs"
    if not blurbs.is_dir():
        return SKIP, "haido_core/vocab/blurbs/ not present yet", []
    # cho phép số nằm trong tên công nghệ: Java 17, S3, EC2, OAuth2, Web3, HTML5, Vue 3
    tech = re.compile(r"[A-Za-z][A-Za-z+#.]*\s?\d+")
    hits = []
    for f in blurbs.rglob("*"):
        if not f.is_file():
            continue
        for i, line in enumerate(read(f).splitlines(), 1):
            stripped = tech.sub("", line)
            if re.search(r"\d|%", stripped):
                hits.append("%s:%d: %s" % (f.relative_to(ROOT).as_posix(), i, line.strip()[:90]))
    return (FAIL if hits else PASS), "scanned blurbs", hits


# ---------------------------------------------------------------- AD-11/AD-18
@gate("AD-11/18", "Privacy: no table stores CV or JD text")
def gate_rieng_tu_khong_luu_van_ban():
    dirs = [d for d in ("haido_core/db", "haido_api", "migrations", "alembic") if (ROOT / d).is_dir()]
    if not dirs:
        return SKIP, "db/migration layer not present yet", []
    bad_cols = r"\b(cv_text|jd_text|resume_text|raw_jd|job_text|pasted_text|cv_content)\b"
    hits = scan(py_files(*dirs), bad_cols, re.I)
    return (FAIL if hits else PASS), "scanned column names", hits


# ---------------------------------------------------------------- AD-25
@gate("AD-25", "Alembic single head")
def gate_ad25_mot_head_alembic():
    vers = None
    for cand in ("migrations/versions", "alembic/versions", "haido_core/db/migrations/versions"):
        if (ROOT / cand).is_dir():
            vers = ROOT / cand
            break
    if vers is None:
        return SKIP, "migration directory not present yet", []
    revs, downs = set(), set()
    for f in vers.glob("*.py"):
        txt = read(f)
        m = re.search(r"^revision(?::\s*str)?\s*=\s*['\"]([^'\"]+)", txt, re.M)
        d = re.search(r"^down_revision(?::\s*[^=]+)?\s*=\s*['\"]([^'\"]+)", txt, re.M)
        if m:
            revs.add(m.group(1))
        if d:
            downs.add(d.group(1))
    heads = sorted(revs - downs)
    if len(revs) == 0:
        return FAIL, "no parsable revisions found", []
    if len(heads) != 1:
        return FAIL, "%d heads found" % len(heads), heads
    return PASS, "%d migrations, %d head" % (len(revs), len(heads)), []


GATES = [v for k, v in sorted(globals().items()) if k.startswith("gate_") and callable(v)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require", nargs="*", default=[],
                    help="gate codes that must really run; SKIP counts as a failure")
    args = ap.parse_args()

    for g in GATES:
        g()

    width = max(len(n) for _, n, _, _ in RESULTS)
    broken = 0
    print("Architecture gates - AD-24\n")
    for code, name, status, detail in RESULTS:
        forced = status == SKIP and code in args.require
        mark = "x" if status == FAIL or forced else ("-" if status == SKIP else "v")
        print(" [%s] %-12s %-*s  %s" % (mark, code, width, name, status + (" (required)" if forced else "")))
        if status == FAIL or forced:
            broken += 1
            for d in detail[:10]:
                print("        %s" % d)
            if len(detail) > 10:
                print("        ... and %d more lines" % (len(detail) - 10))

    n_dat = sum(1 for _, _, s, _ in RESULTS if s == PASS)
    n_bo = sum(1 for _, _, s, _ in RESULTS if s == SKIP)
    print("\n%d gates: %d pass, %d skipped (code not present yet), %d failed" % (len(RESULTS), n_dat, n_bo, broken))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
