#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Chín cổng kiến trúc của AD-24 — chặn merge.

Mỗi cổng là một hàm có tên chứa mã AD hoặc FR, đúng yêu cầu của AD-24.

Ba trạng thái:
  DAT      cổng chạy và không thấy vi phạm
  BO QUA   phần mã mà cổng canh chưa tồn tại — cổng tự bật khi mã xuất hiện
  HONG     có vi phạm, thoát mã 1

Chạy tay:   python tools/gates/check_gates.py
Nghiêm ngặt: python tools/gates/check_gates.py --require AD-1 AD-2 AD-25
             (những cổng nêu tên mà còn BO QUA cũng tính là HONG)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DAT, BOQUA, HONG = "DAT", "BO QUA", "HONG"
RESULTS: list[tuple[str, str, str, list[str]]] = []


def gate(code: str, name: str):
    def deco(fn):
        def run():
            try:
                status, detail, hits = fn()
            except Exception as exc:  # cổng hỏng thì báo, không nuốt
                status, detail, hits = HONG, "cổng lỗi: %r" % (exc,), []
            RESULTS.append((code, name, status, hits if hits else [detail]))
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
@gate("AD-1", "Hướng phụ thuộc không đảo")
def gate_ad1_huong_phu_thuoc():
    checks = [
        ("haido_core/domain", r"^\s*(from|import)\s+(sqlalchemy|dagster|fastapi)\b",
         "domain kéo theo hạ tầng"),
        ("haido_core/steps", r"^\s*(from|import)\s+dagster\b", "steps import Dagster"),
        ("haido_api", r"^\s*(from|import)\s+(dagster|haido_pipeline)\b", "api import pipeline"),
    ]
    present = [d for d, _, _ in checks if (ROOT / d).is_dir()]
    if not present:
        return BOQUA, "chưa có haido_core/ hay haido_api/", []
    hits = []
    for d, pat, why in checks:
        for h in scan(py_files(d), pat, re.M):
            hits.append("%s — %s" % (why, h))
    return (HONG if hits else DAT), "%d thư mục được canh" % len(present), hits


# ---------------------------------------------------------------- AD-2
@gate("AD-2", "Registry đóng tám phép")
def gate_ad2_registry_dong():
    reg = ROOT / "haido_core" / "domain" / "REGISTRY.md"
    if not reg.exists():
        return BOQUA, "chưa có haido_core/domain/REGISTRY.md", []
    txt = read(reg)
    need = ["mapping", "chọn ô", "dân số", "nhóm kỹ năng", "phân vị",
            "phân loại", "so khớp", "xếp thứ tự"]
    missing = [n for n in need if n.lower() not in txt.lower()]
    if missing:
        return HONG, "REGISTRY.md thiếu phép", ["thiếu: " + ", ".join(missing)]
    return DAT, "đủ tám phép", []


# ---------------------------------------------------------------- AD-7
@gate("AD-7", "API không tổng hợp trên bảng job_*")
def gate_ad7_khong_tong_hop_tren_job():
    if not (ROOT / "haido_api").is_dir():
        return BOQUA, "chưa có haido_api/", []
    hits = scan(py_files("haido_api"), r"\bjob_(postings|observations)\b")
    return (HONG if hits else DAT), "quét haido_api/", hits


# ---------------------------------------------------------------- AD-17
@gate("AD-17", "Hình dạng envelope meta")
def gate_ad17_hinh_dang_meta():
    dom = ROOT / "haido_core" / "domain"
    if not dom.is_dir():
        return BOQUA, "chưa có haido_core/domain/", []
    need = ["snapshot_date", "snapshot_status", "sources", "sources_failed",
            "thresholds", "coverage_notes", "n_by_measure", "insufficient_by_measure"]
    blob = "\n".join(read(f) for f in py_files("haido_core/domain"))
    if "class Envelope" not in blob and "Envelope" not in blob:
        return HONG, "không thấy model Envelope trong domain/", []
    missing = [n for n in need if n not in blob]
    return (HONG if missing else DAT), "model Envelope", (["thiếu trường: " + ", ".join(missing)] if missing else [])


# ---------------------------------------------------------------- AD-23
@gate("AD-23", "localStorage dùng danh sách khóa đóng")
def gate_ad23_khoa_dong():
    web = ROOT / "web"
    if not web.is_dir():
        return BOQUA, "chưa có web/", []
    files = [f for f in web.rglob("*.ts") if "node_modules" not in f.parts]
    files += [f for f in web.rglob("*.tsx") if "node_modules" not in f.parts]
    allow = re.compile(r"storage|haido-keys", re.I)
    hits = [h for h in scan(files, r"localStorage\.(get|set|remove)Item")
            if not allow.search(h.split(":")[0])]
    return (HONG if hits else DAT), "gọi localStorage ngoài module khóa đóng", hits


# ---------------------------------------------------------------- FR-25/31/47
@gate("FR-25/31/47", "Câu chữ bị cấm")
def gate_fr_cau_chu_bi_cam():
    targets = [d for d in ("web", "haido_core", "haido_api") if (ROOT / d).is_dir()]
    if not targets:
        return BOQUA, "chưa có mã nguồn sản phẩm", []
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
    return (HONG if hits else DAT), "%d file được quét" % len(files), hits


# ---------------------------------------------------------------- FR-24
@gate("FR-24", "Lời dẫn không chứa số")
def gate_fr24_loi_dan_khong_so():
    blurbs = ROOT / "haido_core" / "vocab" / "blurbs"
    if not blurbs.is_dir():
        return BOQUA, "chưa có haido_core/vocab/blurbs/", []
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
    return (HONG if hits else DAT), "quét lời dẫn", hits


# ---------------------------------------------------------------- AD-11/AD-18
@gate("AD-11/18", "Riêng tư: không bảng nào nhận văn bản CV hay JD")
def gate_rieng_tu_khong_luu_van_ban():
    dirs = [d for d in ("haido_core/db", "haido_api", "migrations", "alembic") if (ROOT / d).is_dir()]
    if not dirs:
        return BOQUA, "chưa có tầng db/migration", []
    bad_cols = r"\b(cv_text|jd_text|resume_text|raw_jd|job_text|pasted_text|cv_content)\b"
    hits = scan(py_files(*dirs), bad_cols, re.I)
    return (HONG if hits else DAT), "quét tên cột", hits


# ---------------------------------------------------------------- AD-25
@gate("AD-25", "Alembic đúng một head")
def gate_ad25_mot_head_alembic():
    vers = None
    for cand in ("migrations/versions", "alembic/versions", "haido_core/db/migrations/versions"):
        if (ROOT / cand).is_dir():
            vers = ROOT / cand
            break
    if vers is None:
        return BOQUA, "chưa có thư mục migration", []
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
    if len(heads) > 1:
        return HONG, "có %d head" % len(heads), heads
    return DAT, "%d migration, %d head" % (len(revs), len(heads)), []


GATES = [v for k, v in sorted(globals().items()) if k.startswith("gate_") and callable(v)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require", nargs="*", default=[],
                    help="mã cổng bắt buộc phải chạy thật, BO QUA cũng tính là hỏng")
    args = ap.parse_args()

    for g in GATES:
        g()

    width = max(len(n) for _, n, _, _ in RESULTS)
    broken = 0
    print("Chín cổng kiến trúc — AD-24\n")
    for code, name, status, detail in RESULTS:
        forced = status == BOQUA and code in args.require
        mark = "x" if status == HONG or forced else ("-" if status == BOQUA else "v")
        print(" [%s] %-12s %-*s  %s" % (mark, code, width, name, status + (" (bắt buộc)" if forced else "")))
        if status == HONG or forced:
            broken += 1
            for d in detail[:10]:
                print("        %s" % d)
            if len(detail) > 10:
                print("        ... và %d dòng nữa" % (len(detail) - 10))

    n_dat = sum(1 for _, _, s, _ in RESULTS if s == DAT)
    n_bo = sum(1 for _, _, s, _ in RESULTS if s == BOQUA)
    print("\n%d cổng: %d đạt, %d bỏ qua (chưa có mã), %d hỏng" % (len(RESULTS), n_dat, n_bo, broken))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
