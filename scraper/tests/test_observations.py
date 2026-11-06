"""job_observations must mean "listed that day", across several days.

Crawler and redact tests need no database. The ingest tests need a throwaway
Postgres in TEST_DATABASE_URL and skip without one; never point it at production,
every test drops the tables.
"""

import collections
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import clean  # noqa: E402
import dedupe  # noqa: E402
import ingest  # noqa: E402
import pipeline  # noqa: E402
import redact  # noqa: E402
from crawlers import careerlink, itnavi, itviec, topdev, vietnamworks, zalo  # noqa: E402
from crawlers.base import write_jsonl  # noqa: E402
from crawlers.polite import USER_AGENT, BlockedError, BudgetExhausted, PoliteClient  # noqa: E402


class Resp:
    def __init__(self, text="", data=None):
        self.text, self._data = text, data

    def json(self):
        return self._data


def seen_doc(source, snapshot="2026-11-05"):
    return json.loads(Path(f"data/seen/{snapshot}/{source}.json").read_text(encoding="utf-8"))


def listing(ids):
    return "".join(f'<div class="jsl-item" data-id="{i}"></div>' for i in ids)


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HAIDO_SNAPSHOT", "2026-11-05")
    return tmp_path


def fake_itnavi(pages, block_on_page=None):
    class Client:
        def __init__(self, **_):
            self.count = 0

        def get(self, url):
            if "get-job-by-id" in url:
                job_id = int(url.rsplit("/", 1)[1])
                return Resp(data={"success": True, "data": {
                    "job_id": job_id, "job_slug": f"https://x/{job_id}", "job_content": "<p>d</p>"}})
            page = int(url.split("page=")[1])
            if page == block_on_page:
                raise BlockedError("HTTP 403")
            return Resp(listing(pages.get(page, [])))
    return Client


def run_crawler(module, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["crawler", *argv])
    module.main()


def test_zalo_url_survives_the_random_slug_suffix():
    one = zalo.parse_job({"slug": "software-engineer-media-n-m6CZGWB9EmtndYn_", "name": "x"}, "t")
    two = zalo.parse_job({"slug": "software-engineer-media-n-uG8IPBEQv0zXhC9R", "name": "x"}, "t")
    assert one["job_url"] == two["job_url"] == "https://zalo.careers/job/software-engineer-media"


def test_itnavi_known_job_still_listed_is_observed_without_a_new_raw_row(workdir, monkeypatch):
    write_jsonl(Path("data/raw/itnavi.jsonl"), [{"job_id": 1, "job_url": "https://x/1"}])
    monkeypatch.setattr(itnavi, "PoliteClient", fake_itnavi({1: [1, 2]}))
    run_crawler(itnavi, monkeypatch)
    doc = seen_doc("itnavi")
    assert sorted(doc["job_urls"]) == ["https://x/1", "https://x/2"]
    assert doc["listing_complete"] is True


def test_itnavi_detail_limit_does_not_stop_the_listing_walk(workdir, monkeypatch):
    write_jsonl(Path("data/raw/itnavi.jsonl"), [{"job_id": 9, "job_url": "https://x/9"}])
    monkeypatch.setattr(itnavi, "PoliteClient", fake_itnavi({1: [1, 2], 2: [9]}))
    run_crawler(itnavi, monkeypatch, "--limit", "1")
    doc = seen_doc("itnavi")
    assert "https://x/9" in doc["job_urls"]
    assert doc["unresolved"] == 1
    assert doc["listing_complete"] is True


def test_itnavi_block_mid_walk_is_an_incomplete_run(workdir, monkeypatch):
    monkeypatch.setattr(itnavi, "PoliteClient", fake_itnavi({1: [1]}, block_on_page=2))
    run_crawler(itnavi, monkeypatch)
    doc = seen_doc("itnavi")
    assert doc["job_urls"] == ["https://x/1"]
    assert doc["listing_complete"] is False
    assert "403" in doc["error"]


def careerlink_page(ids):
    return "".join(f'<a href="/tim-viec-lam/job/{i}">x</a>' for i in ids)


def fake_careerlink(pages, budget=None):
    class Client:
        def __init__(self, **_):
            self.count = 0

        def get(self, url):
            self.count += 1
            if budget is not None and self.count > budget:
                raise BudgetExhausted("used")
            if "/tim-viec-lam/" in url:
                job = {"@type": "JobPosting", "title": "t", "description": "<p>d</p>"}
                return Resp('<script type="application/ld+json">' + json.dumps(job) + "</script>")
            page = int(url.split("page=")[1]) if "page=" in url else 1
            return Resp(careerlink_page(pages.get((url.split("?")[0].rsplit("/", 1)[1], page), [])))
    return Client


def test_careerlink_rewalks_the_listing_every_run(workdir, monkeypatch):
    base = "https://www.careerlink.vn/tim-viec-lam/job/"
    write_jsonl(Path("data/raw/careerlink.jsonl"), [{"job_url": base + "1"}])
    monkeypatch.setattr(careerlink, "PoliteClient", fake_careerlink({("19", 1): [1], ("19", 2): [2], ("130", 1): [1]}))
    run_crawler(careerlink, monkeypatch, "--force")
    doc = seen_doc("careerlink")
    assert sorted(doc["job_urls"]) == [base + "1", base + "2"]
    assert doc["listing_complete"] is True


def test_careerlink_budget_during_listing_is_an_incomplete_run(workdir, monkeypatch):
    monkeypatch.setattr(careerlink, "PoliteClient", fake_careerlink({("19", 1): [1], ("19", 2): [2]}, budget=1))
    run_crawler(careerlink, monkeypatch, "--force")
    assert seen_doc("careerlink")["listing_complete"] is False


def test_careerlink_dead_detail_does_not_stop_the_run(workdir, monkeypatch):
    base_client = fake_careerlink({("19", 1): [1, 2]})

    class Client(base_client):
        def get(self, url):
            if url.endswith("/job/1"):
                raise requests.HTTPError("404")
            return super().get(url)

    monkeypatch.setattr(careerlink, "PoliteClient", Client)
    run_crawler(careerlink, monkeypatch, "--force")
    rows = [json.loads(x) for x in Path("data/raw/careerlink.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["job_url"].rsplit("/", 1)[1] for r in rows] == ["2"]


class FakePage:
    """Serves listing HTML by page number and a detail page for anything else."""

    def __init__(self, pages, card, blocked_on=None):
        self.pages, self.card, self.blocked_on, self.html = pages, card, blocked_on, ""
        self.details = 0

    def goto(self, url, **_):
        if "detail" in url:
            self.details += 1
            job = {"@type": "JobPosting", "description": "<p>mo ta</p>"}
            self.html = '<script type="application/ld+json">' + json.dumps(job) + "</script>"
            return
        n = int(url.split("page=")[1]) if "page=" in url else 1
        if n == self.blocked_on:
            self.html = "<html><title>Just a moment...</title></html>"
            return
        self.html = "".join(self.card(i) for i in self.pages.get(n, []))

    def content(self):
        return self.html

    def wait_for_timeout(self, _):
        pass

    def wait_for_selector(self, *_, **__):
        pass

    def close(self):
        pass


def itviec_card(i):
    return f'<div class="job-card"><h3><a href="/it-jobs/detail-{i}">t{i}</a></h3></div>'


@pytest.fixture
def fake_browser(monkeypatch):
    import contextlib

    def install(module, page):
        @contextlib.contextmanager
        def browser(headless=True):
            class Ctx:
                def new_page(self):
                    return page
            yield Ctx()
        monkeypatch.setattr(module, "browser_polite", browser)
        monkeypatch.setattr(module.time, "sleep", lambda _: None)
    return install


@pytest.mark.parametrize("module,card,prefix", [
    (itviec, itviec_card, "https://itviec.com/it-jobs/detail-"),
])
def test_browser_crawlers_keep_walking_past_the_detail_limit(workdir, monkeypatch, fake_browser, module, card, prefix):
    page = FakePage({1: [1, 2], 2: [3]}, card)
    fake_browser(module, page)
    run_crawler(module, monkeypatch, "--limit", "1")
    doc = seen_doc(module.__name__.split(".")[1])
    assert sorted(doc["job_urls"]) == [prefix + "1", prefix + "2", prefix + "3"]
    assert doc["listing_complete"] is True
    assert page.details == 1


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_browser_crawlers_block_is_an_incomplete_run(workdir, monkeypatch, fake_browser, module, card):
    fake_browser(module, FakePage({1: [1]}, card, blocked_on=2))
    run_crawler(module, monkeypatch)
    doc = seen_doc(module.__name__.split(".")[1])
    assert len(doc["job_urls"]) == 1
    assert doc["listing_complete"] is False


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_browser_crawlers_empty_first_page_is_not_a_complete_run(workdir, monkeypatch, fake_browser, module, card):
    fake_browser(module, FakePage({}, card))
    run_crawler(module, monkeypatch)
    assert seen_doc(module.__name__.split(".")[1])["listing_complete"] is False


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_browser_crawlers_keep_observations_when_details_die(workdir, monkeypatch, fake_browser, module, card):
    class DiesOnDetail(FakePage):
        def goto(self, url, **kw):
            if "detail" in url:
                self.html = "<html><title>Just a moment...</title></html>"
                return
            super().goto(url, **kw)

    fake_browser(module, DiesOnDetail({1: [1, 2]}, card))
    run_crawler(module, monkeypatch)
    doc = seen_doc(module.__name__.split(".")[1])
    assert len(doc["job_urls"]) == 2
    assert doc["listing_complete"] is True


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_browser_crawlers_slow_page_is_not_the_end_of_the_listing(workdir, monkeypatch, fake_browser, module, card):
    class SlowPageTwo(FakePage):
        blank_left = 1

        def goto(self, url, **kw):
            super().goto(url, **kw)
            if url.endswith("page=2") and self.blank_left:
                self.blank_left -= 1
                self.html = "<html></html>"

    fake_browser(module, SlowPageTwo({1: [1], 2: [2], 3: [3]}, card))
    run_crawler(module, monkeypatch, "--skip-details")
    doc = seen_doc(module.__name__.split(".")[1])
    assert len(doc["job_urls"]) == 3
    assert doc["listing_complete"] is True


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_crashed_tab_is_replaced_and_writes_no_empty_row(workdir, monkeypatch, fake_browser, module, card):
    class CrashesOnce(FakePage):
        crashed, crashes_left = False, 1

        def goto(self, url, **kw):
            if self.crashed:
                raise RuntimeError("Page.goto: Page crashed")
            if "detail" in url and self.crashes_left:
                self.crashes_left, self.crashed = 0, True
                raise RuntimeError("Page.goto: Page crashed")
            super().goto(url, **kw)

        def close(self):
            self.crashed = False

    fake_browser(module, CrashesOnce({1: [1, 2, 3]}, card))
    run_crawler(module, monkeypatch)
    name = module.__name__.split(".")[1]
    rows = [json.loads(x) for x in Path(f"data/raw/{name}.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2  # the crashed one waits for the next run, the others still load
    assert all(r["description"] for r in rows)


@pytest.mark.parametrize("module,card", [(itviec, itviec_card)])
def test_browser_that_stays_dead_stops_without_writing(workdir, monkeypatch, fake_browser, module, card):
    class AlwaysDead(FakePage):
        def goto(self, url, **kw):
            if "detail" in url:
                raise RuntimeError("Page.goto: Page crashed")
            super().goto(url, **kw)

    fake_browser(module, AlwaysDead({1: list(range(30))}, card))
    run_crawler(module, monkeypatch)
    name = module.__name__.split(".")[1]
    assert not Path(f"data/raw/{name}.jsonl").exists()
    assert len(seen_doc(name)["job_urls"]) == 30


def topdev_html(ids, last, total):
    links = "".join(f'<a href="/detail-jobs/{t}-{i}">{t}</a>' for i, t in ids)
    return f'{links}<script>x({{\\"last_page\\":{last},\\"total\\":{total}}})</script>'


def fake_topdev(category, listing, block_listing_page=None):
    class Client:
        def __init__(self, **_):
            pass

        def get(self, url):
            if "/detail-jobs/" in url:
                job = {"@type": "JobPosting", "description": "<p>mo ta</p>"}
                return Resp('<script type="application/ld+json">' + json.dumps(job) + "</script>")
            page = int(url.split("page=")[1])
            source = category if "job_categories_ids" in url else listing
            if source is listing and page == block_listing_page:
                raise BlockedError("HTTP 403")
            return Resp(topdev_html(source[page - 1], len(source), sum(len(p) for p in source)))
    return Client


TD = "https://topdev.vn/detail-jobs/"
IT_PAGE = [(1, "Chuyen vien phan tich")]
MIXED_PAGES = [[(1, "Chuyen vien phan tich"), (2, "Ke toan noi bo")], [(3, "Backend Developer"), (4, "Nhan vien ban hang")]]


def test_topdev_keeps_it_category_and_keyword_jobs_only(workdir, monkeypatch):
    monkeypatch.setattr(topdev, "PoliteClient", fake_topdev([IT_PAGE], MIXED_PAGES))
    run_crawler(topdev, monkeypatch)
    doc = seen_doc("topdev")
    assert sorted(doc["job_urls"]) == [TD + "Backend Developer-3", TD + "Chuyen vien phan tich-1"]
    assert doc["listing_complete"] is True
    rows = Path("data/raw/topdev.jsonl").read_text(encoding="utf-8")
    assert "Ke toan" not in rows and "ban hang" not in rows


def test_topdev_walks_to_last_page_not_to_an_empty_page(workdir, monkeypatch):
    monkeypatch.setattr(topdev, "PoliteClient", fake_topdev([IT_PAGE], MIXED_PAGES))
    run_crawler(topdev, monkeypatch, "--skip-details")
    assert TD + "Backend Developer-3" in seen_doc("topdev")["job_urls"]


def test_topdev_block_mid_walk_is_an_incomplete_run(workdir, monkeypatch):
    monkeypatch.setattr(topdev, "PoliteClient", fake_topdev([IT_PAGE], MIXED_PAGES, block_listing_page=2))
    run_crawler(topdev, monkeypatch, "--skip-details")
    doc = seen_doc("topdev")
    assert doc["listing_complete"] is False and "403" in doc["error"]


def test_topdev_too_few_jobs_met_is_an_incomplete_run(workdir, monkeypatch):
    class Short(fake_topdev([IT_PAGE], MIXED_PAGES)):
        def get(self, url):
            r = super().get(url)
            r.text = r.text.replace('\\"total\\":4', '\\"total\\":400')
            return r

    monkeypatch.setattr(topdev, "PoliteClient", Short)
    run_crawler(topdev, monkeypatch, "--skip-details")
    assert seen_doc("topdev")["listing_complete"] is False


def zero_results_on(page_no, times):
    class Client(fake_topdev([IT_PAGE], MIXED_PAGES)):
        left = times

        def get(self, url):
            if "job_categories_ids" not in url and url.endswith(f"page={page_no}") and Client.left:
                Client.left -= 1
                return Resp(topdev_html([(9, "Ke toan goi y")], 0, 0))
            return super().get(url)
    return Client


def test_topdev_zero_results_hiccup_is_retried_not_the_end(workdir, monkeypatch):
    monkeypatch.setattr(topdev.time, "sleep", lambda _: None)
    monkeypatch.setattr(topdev, "PoliteClient", zero_results_on(2, 1))
    run_crawler(topdev, monkeypatch, "--skip-details")
    doc = seen_doc("topdev")
    assert TD + "Backend Developer-3" in doc["job_urls"]
    assert doc["listing_complete"] is True


def test_topdev_zero_results_that_persist_are_an_incomplete_run(workdir, monkeypatch):
    monkeypatch.setattr(topdev.time, "sleep", lambda _: None)
    monkeypatch.setattr(topdev, "PoliteClient", zero_results_on(2, 99))
    run_crawler(topdev, monkeypatch, "--skip-details")
    doc = seen_doc("topdev")
    assert doc["listing_complete"] is False
    assert "no results" in doc["error"]


def test_vietnamworks_page_cap_is_an_incomplete_run(workdir, monkeypatch):
    class Client:
        def __init__(self, **_):
            pass

        def post(self, url, json):
            return Resp(data={"data": [{"jobUrl": f"https://v/{json['page']}", "jobTitle": "t"}]})

    monkeypatch.setattr(vietnamworks, "PoliteClient", Client)
    run_crawler(vietnamworks, monkeypatch, "--pages", "2")
    doc = seen_doc("vietnamworks")
    assert doc["listing_complete"] is False
    assert len(doc["job_urls"]) == 2


@pytest.mark.parametrize("text,kind", [
    ("Gửi CV về hr.hoa@cong-ty.vn nhé", "email"),
    ("Gọi 0912 345 678", "phone"),
    ("Hotline +84 912.345.678", "phone"),
    ("Tổng đài 024 3456 7890", "phone"),
    ("Zalo: 912345678", "zalo"),
    ("Liên hệ: chị Nguyễn Thị Hoa để biết thêm", "name"),
])
def test_redact_removes_contact_details(text, kind):
    counts = collections.Counter()
    out = redact.scrub_text(text, counts)
    assert counts[kind] == 1
    assert redact.MASK in out


def test_redact_keeps_job_url_and_ordinary_numbers():
    counts = collections.Counter()
    row = {"job_url": "https://v/java-0912345678-jv", "salary": "10000000-20000000 VND",
           "description": "Java 17, 3 năm kinh nghiệm, lương 20000000 đồng, làm việc nhóm"}
    assert redact.scrub_row(row, counts) == row
    assert sum(counts.values()) == 0


def topcv_card(i):
    return f'<div class="job-item-search-result" data-job-id="{i}"><h3 class="title"><a href="/viec-lam/x/{i}.html">t</a></h3></div>'


@pytest.fixture
def topcv(workdir, monkeypatch):
    import types

    monkeypatch.setitem(sys.modules, "nodriver", types.ModuleType("nodriver"))
    import importlib

    import crawlers.topcv as module
    importlib.reload(module)
    monkeypatch.setattr(module, "DB_PATH", "cv.db")
    return module


def walk_topcv(module, pages):
    class Client:
        async def fetch(self, url, is_listing=False):
            value = pages.get(int(url.split("page=")[1]), [])
            return "<html>" + "".join(topcv_card(i) for i in value) if isinstance(value, list) else value

    import asyncio

    return asyncio.run(module.crawl_listing_pages(module.init_db(), Client()))


def test_topcv_walks_past_two_hundred_pages(topcv):
    seen, complete = walk_topcv(topcv, {n: [n] for n in range(1, 251)})
    assert len(seen) == 250 and complete is True


def test_topcv_repeated_last_page_ends_the_walk(topcv):
    pages = {n: [min(n, 3)] for n in range(1, 50)}
    seen, complete = walk_topcv(topcv, pages)
    assert len(seen) == 3 and complete is True


@pytest.mark.parametrize("blocked", ["<title>Just a moment...</title>", None])
def test_topcv_block_is_not_the_end_of_the_listing(topcv, blocked):
    seen, complete = walk_topcv(topcv, {1: [1], 2: blocked})
    assert len(seen) == 1 and complete is False


def test_topcv_empty_first_page_is_not_a_complete_run(topcv):
    assert walk_topcv(topcv, {1: []}) == ([], False)


# --------------------------------------------------------------- real Postgres

DSN = os.environ.get("TEST_DATABASE_URL")
needs_db = pytest.mark.skipif(not DSN, reason="TEST_DATABASE_URL not set")


@pytest.fixture
def conn():
    from db import connect
    with connect(DSN) as c:
        with c.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS jobs, job_observations, source_runs, job_content_versions")
            cur.execute((Path(__file__).resolve().parents[1] / "schema.sql").read_text(encoding="utf-8"))
        c.commit()
        yield c


def day(conn, snapshot, urls, complete=True, source="zalo"):
    records = [ingest.to_record({"job_url": u, "site": source, "title": u}) for u in urls]
    seen = {source: {"job_urls": urls, "listing_complete": complete, "unresolved": 0,
                     "error": None if complete else "blocked"}}
    ingest.ingest_snapshot(conn, snapshot, records, seen)


def observed(conn, snapshot):
    with conn.cursor() as cur:
        cur.execute("SELECT job_url FROM job_observations WHERE snapshot_date = %s ORDER BY 1", (snapshot,))
        return [r["job_url"] for r in cur.fetchall()]


@needs_db
def test_job_taken_down_stops_being_observed(conn):
    day(conn, "2026-11-05", ["a", "b"])
    day(conn, "2026-11-06", ["a"])
    assert observed(conn, "2026-11-06") == ["a"]
    with conn.cursor() as cur:
        assert ingest.gone_jobs(cur, "zalo", "2026-11-06") == ["b"]
        cur.execute("SELECT count(*) AS n FROM jobs")
        assert cur.fetchone()["n"] == 2


@needs_db
def test_job_still_open_gets_one_observation_per_day(conn):
    for d in ("2026-11-05", "2026-11-06", "2026-11-07"):
        day(conn, d, ["a"])
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM job_observations WHERE job_url = 'a'")
        assert cur.fetchone()["n"] == 3


@needs_db
def test_incomplete_run_does_not_mark_jobs_gone(conn):
    day(conn, "2026-11-05", ["a", "b"])
    day(conn, "2026-11-06", ["a"], complete=False)
    day(conn, "2026-11-07", ["a"])
    with conn.cursor() as cur:
        assert ingest.gone_jobs(cur, "zalo", "2026-11-06") == []
        # the complete run compares with the last complete run, skipping the partial one
        assert ingest.gone_jobs(cur, "zalo", "2026-11-07") == ["b"]


@needs_db
def test_listing_that_shrinks_by_half_is_not_trusted(conn):
    day(conn, "2026-11-05", ["a", "b", "c", "d", "e"])
    day(conn, "2026-11-06", ["a", "b"])
    with conn.cursor() as cur:
        assert ingest.gone_jobs(cur, "zalo", "2026-11-06") == []
        cur.execute("SELECT listing_complete, error FROM source_runs WHERE snapshot_date = '2026-11-06'")
        row = cur.fetchone()
    assert row["listing_complete"] is False and "shrank" in row["error"]


def jd_day(conn, snapshot, description):
    rec = ingest.to_record({"job_url": "a", "site": "zalo", "description": description})
    ingest.ingest_snapshot(conn, snapshot, [rec], {})


def test_content_hash_ignores_whitespace_only():
    assert ingest.content_hash("Java  17\n\nSQL") == ingest.content_hash(" Java 17 SQL ")
    assert ingest.content_hash("Java 17") != ingest.content_hash("Java 21")
    assert ingest.content_hash("  ") is None


@needs_db
def test_changed_description_is_counted_once_and_not_on_first_sight(conn):
    jd_day(conn, "2026-11-05", "Java 17")
    with conn.cursor() as cur:
        assert ingest.changed_jobs(cur, "2026-11-05") == {}
    jd_day(conn, "2026-11-06", "Java   17")  # reflowed, not changed
    with conn.cursor() as cur:
        assert ingest.changed_jobs(cur, "2026-11-06") == {}
    jd_day(conn, "2026-11-07", "Java 21")
    jd_day(conn, "2026-11-07", "Java 21")  # rerun the same day
    with conn.cursor() as cur:
        assert ingest.changed_jobs(cur, "2026-11-07") == {"zalo": 1}


@needs_db
def test_crashed_source_is_recorded_as_incomplete(conn, tmp_path):
    seen = ingest.load_seen(tmp_path, "2026-11-05", ["zalo"])
    ingest.ingest_snapshot(conn, "2026-11-05", [], seen)
    with conn.cursor() as cur:
        cur.execute("SELECT listing_complete, seen_count, error FROM source_runs")
        row = cur.fetchone()
    assert row["listing_complete"] is False and row["seen_count"] == 0 and "did not finish" in row["error"]


@needs_db
def test_rerun_same_day_changes_nothing(conn):
    day(conn, "2026-11-05", ["a"])
    day(conn, "2026-11-05", ["a"])
    assert observed(conn, "2026-11-05") == ["a"]


@needs_db
def test_ingest_never_touches_extraction_columns(conn):
    import extract

    day(conn, "2026-11-05", ["a"])
    row = extract.to_output_row(
        {"job_url": "a", "description_consolidated": "sach"},
        {"title_cleaned": "Dev", "tech_stack": ["Java"], "keywords": ["k"], "skills_raw": ["học máy"],
         "years_experience_min": 2, "years_experience_max": 3, "title_category": "Backend",
         "seniority_category": "Junior", "location_category": "Ha Noi", "work_model_category": "Hybrid",
         "is_it_job": True, "it_confidence": 0.9}, "m")
    extract.write_db([row], conn=conn)
    day(conn, "2026-11-06", ["a"])  # next day's raw row knows nothing of extraction
    with conn.cursor() as cur:
        cur.execute("SELECT tech_stack, skills_raw, title_category, is_it_job, description_consolidated FROM jobs")
        got = cur.fetchone()
    assert got == {"tech_stack": ["Java"], "skills_raw": ["học máy"], "title_category": "Backend",
                   "is_it_job": True, "description_consolidated": "sach"}


@needs_db
def test_extract_does_not_create_rows(conn):
    import extract

    row = extract.to_output_row({"job_url": "unknown"}, {}, "m")
    extract.write_db([row], conn=conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM jobs")
        assert cur.fetchone()["n"] == 0


def test_fr2_user_agent_has_team_contact_email():
    assert "hoangduy20407@gmail.com" in USER_AGENT
    assert PoliteClient().session.headers["User-Agent"] == USER_AGENT


def test_fr2_browser_crawlers_send_the_same_user_agent(monkeypatch):
    import contextlib
    import types

    from crawlers import browser_polite

    captured = {}

    class Context:
        def close(self):
            pass

    class Browser:
        def new_context(self, **kwargs):
            captured.update(kwargs)
            return Context()

        def close(self):
            pass

    @contextlib.contextmanager
    def sync_playwright():
        yield SimpleNamespace(chromium=SimpleNamespace(launch=lambda **_: Browser()))

    fake = types.ModuleType("playwright.sync_api")
    fake.sync_playwright = sync_playwright
    monkeypatch.setitem(sys.modules, "playwright", types.ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", fake)

    with browser_polite.browser_polite():
        pass

    assert captured["user_agent"] == USER_AGENT


def test_fr2_robots_rule_for_our_bot_still_applies_with_contact_in_user_agent(monkeypatch):
    robots = "User-agent: HaiDoIT-research-bot\nDisallow: /private\n"

    class RobotsResp:
        status_code = 200
        headers = {"Content-Type": "text/plain"}
        text = robots

    client = PoliteClient()
    monkeypatch.setattr(client.session, "get", lambda *_, **__: RobotsResp())
    assert not client.allowed("https://x.test/private/1")
    assert client.allowed("https://x.test/public/1")


def run_dedupe_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["dedupe.py", *args])
    dedupe.main()
    path = Path("data/dedup.jsonl")
    return path.read_text(encoding="utf-8")


CONTACT_ROW = {
    "site": "itnavi", "job_url": "https://x/1", "title": "Java", "company": "A",
    "description": "Gửi CV về tuyendung@congty.vn hoặc gọi 0912 345 678",
}


def test_ad21_default_dedupe_after_redact_holds_no_contact_details(workdir, monkeypatch):
    write_jsonl(Path("data/raw/itnavi.jsonl"), [CONTACT_ROW])
    monkeypatch.setattr(sys, "argv", ["redact.py"])
    assert redact.main() == 0

    out = run_dedupe_main(monkeypatch)

    assert json.loads(out)["job_url"] == "https://x/1"
    assert "tuyendung@congty.vn" not in out
    patterns = {kind: rx for kind, rx, _ in redact.PATTERNS}
    assert not patterns["email"].search(out)
    assert not patterns["phone"].search(out)

    monkeypatch.setattr(sys, "argv", ["clean.py"])
    clean.main()
    consolidated = Path("data/consolidated.jsonl").read_text(encoding="utf-8")
    assert json.loads(consolidated)["job_url"] == "https://x/1"
    assert not patterns["email"].search(consolidated)
    assert not patterns["phone"].search(consolidated)


def test_ad21_default_dedupe_never_reads_raw(workdir, monkeypatch):
    write_jsonl(Path("data/raw/itnavi.jsonl"), [CONTACT_ROW])

    assert run_dedupe_main(monkeypatch) == ""


def test_ad21_dedupe_explicit_raw_argument_still_wins(workdir, monkeypatch):
    write_jsonl(Path("elsewhere/itnavi.jsonl"), [CONTACT_ROW])

    assert json.loads(run_dedupe_main(monkeypatch, "--raw", "elsewhere"))["job_url"] == "https://x/1"


def test_ad21_ingest_default_reads_redacted_not_raw(workdir, monkeypatch, capsys):
    write_jsonl(Path("data/raw/itnavi.jsonl"), [CONTACT_ROW])
    monkeypatch.setattr(sys, "argv", ["ingest.py", "--dry-run", "--snapshot", "2026-11-05"])

    assert ingest.main() == 0

    assert "jobs    : 0 rows from data/redacted" in capsys.readouterr().out


def test_ad21_daily_dedupe_command_reads_redacted(monkeypatch):
    commands = []

    def fake_run(cmd, **_):
        commands.append(cmd)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(pipeline.subprocess, "run", fake_run)

    assert pipeline.run_dedupe()
    assert commands[0][commands[0].index("--raw") + 1] == "data/redacted"


def test_ad21_extract_input_is_never_a_raw_file():
    import extract

    assert extract.IN_CANDIDATES == ["data/consolidated.jsonl", "data/dedup.jsonl"]
