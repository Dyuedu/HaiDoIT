"""Đo luật cũ (v1), luật mới (#283) và bước trích (Haiku) trên mẫu tự gán nhãn. In bảng Markdown.

    HAIDO_EVAL_DATABASE_URL=postgresql+psycopg://... PYTHONPATH=. uv run python tools/classify_eval/evaluate.py

`labels.csv` chỉ có mã băm URL và nhãn tay (vai trò, số năm tối thiểu; `?` là không đọc được, trống là tin không ghi).
Văn bản JD chỉ được đọc từ DB vào bộ nhớ, không ghi ra đâu.
"""

import csv
import os
import sys
from collections import Counter
from pathlib import Path

from sqlalchemy import create_engine, text

from haido_core.config import load_classify_config, load_rules
from haido_core.db.scraper_source import SourceFactsRow
from haido_core.domain.classify import NON_IT
from haido_core.domain.registry import PostingFacts
from haido_core.steps.ingest import FactLabeler

sys.path.insert(0, str(Path(__file__).parent))
from classify_v1 import RuleClassifier as V1Classifier  # noqa: E402
from classify_v1 import default_classify_config as v1_config  # noqa: E402
from sample import choose, holdout, postings, url_key  # noqa: E402

HAIKU = {
    "Backend": "Backend", "Frontend": "Frontend", "Fullstack": "Fullstack", "Mobile": "Mobile",
    "Data Analyst / BI": "Data Analyst/BI", "Data Engineer": "Data Engineer", "AI / ML Engineer": "AI/ML Engineer",
    "Embedded": "Embedded", "DevOps / SRE / Cloud": "DevOps", "QA / Testing": "QA/Tester",
    "Product / BA / Agile": "BA/PO/PM", "Security / Cyber": "Security", "Infrastructure / IT Support": "Hạ tầng/IT support",
    "UI/UX Design": "UI/UX", "Game Development": "Game", "Other": "Other",
}  # fmt: skip


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "—"


def main() -> None:
    engine = create_engine(os.environ["HAIDO_EVAL_DATABASE_URL"])
    held = len(sys.argv) > 1 and sys.argv[1] == "holdout"
    name = "labels_holdout.csv" if held else "labels.csv"
    labels = {r["key"]: r for r in csv.DictReader(open(Path(__file__).parent / name, encoding="utf-8"))}
    every = postings(engine)
    sample = holdout(every) if held else choose(every)
    by_key = {url_key(r[0]): r for r in sample}
    random_keys = {url_key(r[0]) for r in (sample if held else sample[:120])}
    with engine.connect() as conn:
        extra = {
            r[0]: r[1:]
            for r in conn.execute(
                text(
                    "SELECT job_url, company, location, years_experience_min, title_category, is_it_job, prompt_version "
                    "FROM public.jobs WHERE job_url = ANY(:u)"
                ),
                {"u": [by_key[k][0] for k in labels]},
            )
        }
    cfg, rules = load_classify_config(), load_rules()
    labeler, v1 = FactLabeler(cfg), V1Classifier(v1_config())
    rows = []
    for key, lab in labels.items():
        url, site, title, job_level, exp_level, desc = by_key[key]
        company, location, haiku_years, category, is_it, prompt = extra[url]
        hy = None if haiku_years is None else float(haiku_years)
        fact = labeler.label(site, SourceFactsRow(url, title, company, location, exp_level, job_level, hy, desc))
        level_text = " ".join(p for p in (job_level, exp_level) if p) or None
        old = v1.label_v1(PostingFacts(title, site, None, level_text, location)).role
        haiku = None if prompt is None else (NON_IT if is_it is False else HAIKU.get(category, "Other"))
        rows.append(dict(key=key, truth=lab["role"], years=lab["years"], v1=old, v2=fact.role, haiku=haiku,
                         v2_years=fact.years_min, haiku_years=hy, random=key in random_keys))

    def code(label: str | None) -> str | None:
        if label is None:
            return None
        if label == NON_IT:
            return NON_IT
        return rules.role_codes.get(cfg.report_as.get(label, label), "?")

    systems = (("Luật cũ", "v1"), ("Luật mới", "v2"), ("Bước trích", "haiku"))
    print(f"Mẫu: {len(rows)} tin ({sum(r['random'] for r in rows)} ngẫu nhiên, "
          f"{sum(r['truth'] in ('AI/ML Engineer', 'Data Scientist') for r in rows)} AI/ML hoặc khoa học dữ liệu)\n")
    print("| Bộ | Đúng vai trò (nhãn mịn) | Đúng mã trên bản đồ | IT: precision | IT: recall |")
    print("|---|---|---|---|---|")
    for name, k in systems:
        rs = [r for r in rows if r[k] is not None]
        exact = sum(r[k] == r["truth"] for r in rs)
        mapped = sum(code(r[k]) == code(r["truth"]) for r in rs)
        rnd = [r for r in rs if r["random"]]
        tp = sum(r[k] != NON_IT and r["truth"] != NON_IT for r in rnd)
        fp = sum(r[k] != NON_IT and r["truth"] == NON_IT for r in rnd)
        fn = sum(r[k] == NON_IT and r["truth"] != NON_IT for r in rnd)
        print(f"| {name} (n={len(rs)}) | {pct(exact, len(rs))} | {pct(mapped, len(rs))} | {pct(tp, tp + fp)} | "
              f"{pct(tp, tp + fn)} |")
    print("\nIT precision/recall chỉ tính trên phần chọn ngẫu nhiên (phần AI chọn thêm làm lệch tỷ lệ IT).\n")

    roles = [r for r, _ in Counter(r["truth"] for r in rows).most_common()]
    print("| Vai trò (nhãn tay) | n | " + " | ".join(f"{n} P / R" for n, _ in systems) + " |")
    print("|---|---|" + "---|" * len(systems))
    for role in roles:
        cells = []
        for _, k in systems:
            rs = [r for r in rows if r[k] is not None]
            tp = sum(r[k] == role and r["truth"] == role for r in rs)
            pred = sum(r[k] == role for r in rs)
            true = sum(r["truth"] == role for r in rs)
            cells.append(f"{pct(tp, pred)} / {pct(tp, true)}")
        print(f"| {role} | {sum(r['truth'] == role for r in rows)} | " + " | ".join(cells) + " |")

    print("\nAI/ML gộp Data Scientist (bước trích không có nhãn Data Scientist):\n")
    ai = {"AI/ML Engineer", "Data Scientist"}
    for name, k in systems:
        rs = [r for r in rows if r[k] is not None]
        tp = sum(r[k] in ai and r["truth"] in ai for r in rs)
        pred = sum(r[k] in ai for r in rs)
        true = sum(r["truth"] in ai for r in rs)
        print(f"- {name}: precision {pct(tp, pred)}, recall {pct(tp, true)} (n thật = {true})")

    yrs = [r for r in rows if r["years"] != "?"]
    print(f"\nSố năm tối thiểu, {len(yrs)} tin đọc được (trống = tin không ghi):\n")
    for name, k in (("Luật mới (đã giải)", "v2_years"), ("Bước trích", "haiku_years")):
        ok = sum((r[k] is None and r["years"] == "") or (r[k] is not None and r["years"] != "" and
                 abs(r[k] - float(r["years"])) < 1e-9) for r in yrs)
        print(f"- {name}: khớp {ok}/{len(yrs)} ({pct(ok, len(yrs))})")

    print("\nTin lệch của luật mới:\n")
    for r in rows:
        if r["v2"] != r["truth"]:
            print(f"- {r['key']}: tay={r['truth']} mới={r['v2']} cũ={r['v1']} trích={r['haiku']}")


if __name__ == "__main__":
    main()
