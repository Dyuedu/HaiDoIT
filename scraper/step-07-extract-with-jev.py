
"""
Step 07: Classify extracted job data into strict standardized categories.

Reads data/step-06-extracted.jsonl and uses Typesafe Jev to map job titles
and full descriptions into fixed categories for analytics.

Outputs:
- data/step-07-classified.jsonl
- data/step-07-classify-cache.jsonl

Needs TYPESAFE_API_KEY in the environment or .env.local.
"""

import argparse
import concurrent.futures
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

from crawlers.base import read_jsonl
from tqdm import tqdm

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
MAX_WORKERS = 20
DESCRIPTION_LIMIT = 12000

CACHE_LOCK = threading.Lock()

CATEGORIES = {
    "title_category": [
        "Backend",
        "Frontend",
        "Fullstack",
        "Mobile",
        "Data / AI / ML",
        "DevOps / SRE / Cloud",
        "QA / Testing",
        "Product / BA / Agile",
        "Security / Cyber",
        "Infrastructure / IT Support",
        "UI/UX Design",
        "Game Development",
        "Other",
    ],
    "seniority_category": [
        "Intern",
        "Fresher / Entry-level",
        "Junior",
        "Mid-level",
        "Senior",
        "Lead / Principal",
        "Manager",
        "Director / Executive",
        "Unknown",
    ],
    "location_category": [
        "Ho Chi Minh",
        "Ha Noi",
        "Da Nang",
        "Other",
    ],
    "work_model_category": [
        "On-site",
        "Hybrid",
        "Remote",
        "Unknown",
    ],
}

QUESTION = {
    field: {
        "type": "choice",
        "instructions": instructions,
        "criteria": criteria,
    }
    for field, instructions, criteria in [
        (
            "title_category",
            "Classify the job's primary function based on its title and responsibilities.",
            {
                "Backend": "Backend engineering, server-side development, APIs, databases.",
                "Frontend": "Frontend or web client development.",
                "Fullstack": "Both frontend and backend engineering.",
                "Mobile": "Mobile application development.",
                "Data / AI / ML": "Data engineering, analytics, data science, AI or machine learning.",
                "DevOps / SRE / Cloud": "DevOps, SRE, cloud engineering or platform operations.",
                "QA / Testing": "Quality assurance, software testing or test automation.",
                "Product / BA / Agile": "Product management, business analysis, project management or Agile roles.",
                "Security / Cyber": "Cybersecurity, information security or application security.",
                "Infrastructure / IT Support": "IT infrastructure, system administration, networking or IT support.",
                "UI/UX Design": "User interface or user experience design.",
                "Game Development": "Game programming or game development.",
                "Other": "Any role that does not fit the categories above.",
            },
        ),
        (
            "seniority_category",
            "Classify seniority using explicit experience requirements, scope and leadership responsibilities.",
            {
                "Intern": "Internship or student placement.",
                "Fresher / Entry-level": "Graduate, fresher or entry-level position.",
                "Junior": "Junior-level individual contributor.",
                "Mid-level": "Intermediate independent contributor.",
                "Senior": "Senior individual contributor.",
                "Lead / Principal": "Technical lead, principal or staff-level role.",
                "Manager": "People or team management role.",
                "Director / Executive": "Director, VP or C-suite executive.",
                "Unknown": "Insufficient evidence to determine seniority.",
            },
        ),
        (
            "location_category",
            "Classify the actual job location, not the company's headquarters. For remote jobs, use the stated eligible work location if available.",
            {
                "Ho Chi Minh": "Ho Chi Minh City, HCMC or Saigon.",
                "Ha Noi": "Hanoi or Ha Noi.",
                "Da Nang": "Da Nang city.",
                "Other": "Any other location, multiple locations without a clear match, or insufficient location information.",
            },
        ),
        (
            "work_model_category",
            "Classify the stated working arrangement. Do not assume remote work just because the listing does not specify an office.",
            {
                "On-site": "Primarily working at the employer's workplace.",
                "Hybrid": "A combination of workplace and remote work.",
                "Remote": "Explicitly remote or work-from-anywhere.",
                "Unknown": "Insufficient evidence to determine the working arrangement.",
            },
        ),
    ]
}


def load_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key

    envfile = Path(".env.local")
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            name, _, value = line.strip().partition("=")
            if name.strip() == "TYPESAFE_API_KEY":
                value = value.strip().strip("\"'")
                if value:
                    return value

    raise SystemExit(
        "Missing TYPESAFE_API_KEY (environment or .env.local)"
    )


def ask_jev(state: str) -> dict:
    body = json.dumps(
        {
            "model": MODEL,
            "state": state,
            "questions": QUESTION,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1000]
        raise RuntimeError(
            f"Jev API error {exc.code} {exc.reason}: {detail}"
        ) from exc


def build_state(row: dict) -> str:
    description = (row.get("description") or "").strip()

    return (
        f"Title: {row.get('title') or 'Unknown'}\n"
        f"Company: {row.get('company') or ''}\n"
        f"Location: {row.get('location') or ''}\n"
        f"Experience: {row.get('experience_level') or ''}\n\n"
        f"Full job description:\n{description[:DESCRIPTION_LIMIT]}"
    )


def parse_classification(response: dict) -> dict:
    """Validate all Jev answers before writing anything to the cache."""
    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ValueError(f"Missing answers in Jev response: {response!r}")

    classification = {}

    for field, allowed_values in CATEGORIES.items():
        answer = answers.get(field)
        if not isinstance(answer, dict):
            raise ValueError(f"Missing answer for {field}")

        value = answer.get("choice")
        if value not in allowed_values:
            raise ValueError(
                f"Invalid {field}: {value!r}; expected one of {allowed_values}"
            )

        classification[field] = value

    return classification


def overwrite(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def process_job(row: dict, cache: dict, cache_path: Path) -> None:
    job_url = row.get("job_url")
    if not job_url:
        print("Skipping row without job_url", file=sys.stderr)
        return

    try:
        response = ask_jev(build_state(row))
        classification = parse_classification(response)

        merged = {
            **row,
            "classification": classification,
        }

        with CACHE_LOCK:
            cache[job_url] = merged
            with cache_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(merged, ensure_ascii=False) + "\n")

    except Exception as exc:
        print(
            f"\nFailed to classify {job_url}: {exc}",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify tech jobs into standardized categories using Jev"
    )
    parser.add_argument(
        "--in", dest="src", default="data/step-06-llm-extracted.jsonl"
    )
    parser.add_argument(
        "--out", default="data/step-07-jev-extracted.jsonl"
    )
    parser.add_argument(
        "--cache", default="data/step-07-llm-extracted-cache.jsonl"
    )
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit must be >= 0")

    load_key()

    rows = read_jsonl(args.src)
    dedup = {}
    for row in rows:
        key = row.get("job_url")
        if key:
            dedup.setdefault(key, row)
    rows = list(dedup.values())

    print(f"{len(rows)} unique jobs", flush=True)

    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    cache = {}
    if cache_path.exists():
        for item in read_jsonl(str(cache_path)):
            key = item.get("job_url")
            classification = item.get("classification")
            if (
                key
                and isinstance(classification, dict)
                and all(
                    classification.get(field) in allowed
                    for field, allowed in CATEGORIES.items()
                )
            ):
                cache[key] = item

    todo = [row for row in rows if row["job_url"] not in cache]
    if args.limit:
        todo = todo[:args.limit]

    print(f"{len(todo)} jobs to classify using Jev ({MODEL})", flush=True)

    if todo:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:
            futures = [
                executor.submit(process_job, row, cache, cache_path)
                for row in todo
            ]

            for _ in tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Classifying jobs",
                unit="job",
            ):
                pass

    # Preserve source order in the final output.
    overwrite(
        Path(args.out),
        [cache.get(row["job_url"], row) for row in rows],
    )

    failed = sum(row["job_url"] not in cache for row in rows)
    print(f"Wrote {args.out}", flush=True)
    if failed:
        print(
            f"{failed} jobs remain unclassified; rerun to retry them.",
            flush=True,
        )


if __name__ == "__main__":
    main()
