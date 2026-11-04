"""Pipeline orchestrator, in the two beats of the architecture spine.

Beat one, every day, no API key: crawl -> redact -> ingest.
Beat two, needs ANTHROPIC_API_KEY: dedupe -> clean -> extract.
If beat two fails, nothing is lost: it reruns tomorrow on what beat one kept.

Usage:
    python pipeline.py                  # both beats
    python pipeline.py crawl            # crawl only
    python pipeline.py redact           # remove contact details
    python pipeline.py ingest           # write jobs and today's observations
    python pipeline.py dedupe           # dedupe only
    python pipeline.py process          # clean + extract
    python pipeline.py crawl --sources zalo,itnavi
    python pipeline.py crawl --skip-details   # listing only for JS sites

Each crawler runs as a subprocess. Failures are logged but do not stop the
pipeline: partial data is better than no data.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

SOURCES = {
    "zalo": {
        "module": "crawlers.zalo",
        "type": "api",
        "has_limit": False,
        "args": [],
    },
    "itnavi": {
        "module": "crawlers.itnavi",
        "type": "api",
        "has_limit": True,
        "args": ["--limit", "300"],
    },
    "careerlink": {
        "module": "crawlers.careerlink",
        "type": "api",
        "has_limit": False,
        "args": ["--force", "--delay", "5"],
    },
    "momo": {
        "module": "crawlers.momo",
        "type": "playwright",
        "has_limit": False,
        "args": [],
    },
    "vietnamworks": {
        "module": "crawlers.vietnamworks",
        "type": "api",
        "has_limit": True,
        "args": [],
    },
    "itviec": {
        "module": "crawlers.itviec",
        "type": "playwright",
        "has_limit": True,
        "args": [],
        "timeout": 6 * 3600,  # no detail limit; the seen file is written before details
    },
    "topdev": {
        "module": "crawlers.topdev",
        "type": "api",
        "has_limit": True,
        "args": [],
        "timeout": 6 * 3600,  # no detail limit; the seen file is written before details
    },
    "topcv": {
        "module": "crawlers.topcv",
        "type": "nodriver",
        "has_limit": False,
        "args": [],
    },
}

API_FIRST = ["zalo", "itnavi", "careerlink", "vietnamworks", "topdev"]
PLAYWRIGHT_SECOND = ["momo", "itviec", "topcv"]
ORDER = API_FIRST + PLAYWRIGHT_SECOND


SCRAPER_DIR = Path(__file__).resolve().parent


def run_crawler(name: str, cfg: dict, extra_args: list[str]) -> bool:
    cmd = [sys.executable, "-m", cfg["module"]] + cfg["args"] + extra_args

    print(f"\n{'='*60}", flush=True)
    print(f"  [{name}] starting -- {cfg['module']}", flush=True)
    print(f"{'='*60}", flush=True)

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    start = time.monotonic()
    try:
        result = subprocess.run(cmd, env=env, cwd=str(SCRAPER_DIR), timeout=cfg.get("timeout", 3600))
    except subprocess.TimeoutExpired:
        print(f"  [{name}] FAILED (timeout)", flush=True)
        return False
    elapsed = time.monotonic() - start

    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"  [{name}] {status} in {elapsed:.0f}s", flush=True)
    return result.returncode == 0


def run_dedupe() -> bool:
    print(f"\n{'='*60}", flush=True)
    print(f"  [dedupe] starting", flush=True)
    print(f"{'='*60}", flush=True)

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    cmd = [sys.executable, "dedupe.py",
           "--raw", "data/redacted", "--out", "data/dedup.jsonl"]
    result = subprocess.run(cmd, env=env, cwd=str(SCRAPER_DIR), timeout=300)
    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"  [dedupe] {status}", flush=True)
    return result.returncode == 0


STEPS = [
    {"name": "clean", "script": "clean.py", "needs_api": None},
    {"name": "extract", "script": "extract.py", "needs_api": "ANTHROPIC_API_KEY"},
]


def run_step(step: dict) -> bool:
    name = step["name"]
    print(f"\n{'='*60}", flush=True)
    print(f"  [step: {name}] starting -- {step['script']}", flush=True)
    print(f"{'='*60}", flush=True)

    api_key = step["needs_api"]
    if api_key and not os.environ.get(api_key):
        print(f"  [step: {name}] SKIPPED -- {api_key} not set", flush=True)
        return False

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    cmd = [sys.executable, step["script"]]
    start = time.monotonic()
    result = subprocess.run(cmd, env=env, cwd=str(SCRAPER_DIR), timeout=3600)
    elapsed = time.monotonic() - start

    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"  [step: {name}] {status} in {elapsed:.0f}s", flush=True)
    return result.returncode == 0


def run_process() -> dict[str, bool]:
    results = {}
    for step in STEPS:
        ok = run_step(step)
        results[step["name"]] = ok
        if not ok:
            print(f"  [process] stopping early -- {step['name']} failed", flush=True)
            break
    return results


def run_script(name: str, script: str) -> bool:
    print(flush=True)
    print(f"  [{name}] starting -- {script}", flush=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run([sys.executable, script], env=env, cwd=str(SCRAPER_DIR), timeout=600)
    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"  [{name}] {status}", flush=True)
    return result.returncode == 0


def count_raw() -> dict[str, int]:
    from crawlers.base import read_jsonl
    counts = {}
    raw = Path("data/raw")
    if raw.exists():
        for f in sorted(raw.glob("*.jsonl")):
            counts[f.stem] = len(read_jsonl(f))
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="HaiDoIT scraper pipeline")
    parser.add_argument("action", nargs="?", default="all",
                        choices=["all", "crawl", "redact", "ingest", "dedupe", "process"])
    parser.add_argument("--sources", type=str, default="",
                        help="comma-separated list of sources (default: all)")
    parser.add_argument("--skip-details", action="store_true",
                        help="pass --skip-details to Playwright crawlers")
    parser.add_argument("--limit", type=int, default=0,
                        help="pass --limit N to each crawler")
    parser.add_argument("--no-headless", action="store_true",
                        help="show browser window for Playwright crawlers")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip()] if args.sources else ORDER
    for s in sources:
        if s not in SOURCES:
            print(f"unknown source: {s}. available: {', '.join(ORDER)}")
            sys.exit(1)

    if args.action in ("all", "crawl"):
        results = {}
        for name in sources:
            cfg = SOURCES[name]
            extra = []
            if cfg["type"] == "nodriver":
                pass
            else:
                if args.skip_details and cfg["type"] == "playwright" and name != "momo":
                    extra.append("--skip-details")
                if args.limit and cfg.get("has_limit"):
                    extra.extend(["--limit", str(args.limit)])
                if args.no_headless and cfg["type"] == "playwright":
                    extra.append("--no-headless")
            results[name] = run_crawler(name, cfg, extra)

        print(f"\n{'='*60}", flush=True)
        print("  CRAWL SUMMARY", flush=True)
        print(f"{'='*60}", flush=True)
        for name, ok in results.items():
            mark = "OK" if ok else "FAILED"
            print(f"  {name:15s} {mark}", flush=True)

        counts = count_raw()
        total = sum(counts.values())
        for name, n in counts.items():
            print(f"  {name:15s} {n:>6d} jobs", flush=True)
        print(f"  {'TOTAL':15s} {total:>6d} jobs", flush=True)

    if args.action in ("all", "redact"):
        if not run_script("redact", "redact.py"):
            sys.exit(1)

    if args.action in ("all", "ingest"):
        if not run_script("ingest", "ingest.py"):
            sys.exit(1)

    if args.action in ("all", "dedupe"):
        run_dedupe()
        dedup = Path("data/dedup.jsonl")
        if dedup.exists():
            from crawlers.base import read_jsonl
            n = len(read_jsonl(dedup))
            print(f"\n  dedup.jsonl: {n} unique jobs", flush=True)

    if args.action in ("all", "process"):
        step_results = run_process()
        print(f"\n{'='*60}", flush=True)
        print("  PROCESS SUMMARY", flush=True)
        print(f"{'='*60}", flush=True)
        for name, ok in step_results.items():
            mark = "OK" if ok else "FAILED/SKIPPED"
            print(f"  {name:15s} {mark}", flush=True)
        if not all(step_results.values()):
            sys.exit(1)


if __name__ == "__main__":
    main()
