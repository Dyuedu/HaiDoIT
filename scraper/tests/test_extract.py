"""extract keeps a paid batch across a kill, and one bad reply does not stop the run."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extract  # noqa: E402


def text_message(text):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


def thinking_only():
    return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking="...")])


class SyncMessages:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies.pop(0)


class Batches:
    def __init__(self, statuses, results_by_id):
        self.statuses = list(statuses)
        self.results_by_id = results_by_id
        self.created = []
        self.retrieved = []

    def create(self, requests):
        self.created.append(requests)
        return SimpleNamespace(id="msgbatch_new")

    def retrieve(self, batch_id):
        self.retrieved.append(batch_id)
        if self.statuses and isinstance(self.statuses[0], Exception):
            raise self.statuses.pop(0)
        status = self.statuses.pop(0) if self.statuses else "ended"
        return SimpleNamespace(
            id=batch_id,
            processing_status=status,
            request_counts=SimpleNamespace(processing=1, succeeded=0, errored=0),
        )

    def results(self, batch_id):
        return self.results_by_id.get(batch_id, [])


def succeeded(custom_id, text):
    return SimpleNamespace(
        custom_id=custom_id,
        result=SimpleNamespace(type="succeeded", message=text_message(text)),
    )


def row(url):
    return {"job_url": url, "title": url}


def test_sync_skips_a_bad_reply_and_raises_the_output_cap(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    messages = SyncMessages([
        text_message("{"),
        thinking_only(),
        text_message('{"is_it_job": true}'),
    ])
    client = SimpleNamespace(messages=messages)
    rows = [row("https://a"), row("https://b"), row("https://c")]
    cache = {}

    extract.run_sync(client, rows, extract.MODEL, cache)

    assert list(cache) == [extract.cache_key(rows[2])]
    assert cache[extract.cache_key(rows[2])]["is_it_job"] is True
    assert [call["max_tokens"] for call in messages.calls] == [extract.MAX_TOKENS] * 3
    assert extract.MAX_TOKENS == 16000
    stored = [json.loads(line) for line in extract.CACHE_PATH.read_text(encoding="utf-8").splitlines()]
    assert [item["key"] for item in stored] == [extract.cache_key(rows[2])]


def test_batch_id_is_stored_before_polling(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(extract.time, "sleep", lambda _seconds: None)
    seen = {}

    class Watching(Batches):
        def retrieve(self, batch_id):
            saved = json.loads(extract.PENDING_PATH.read_text(encoding="utf-8"))
            seen["batch_id"] = saved["batch_id"]
            seen["key"] = saved["items"][0]["key"]
            return super().retrieve(batch_id)

    one = row("https://a")
    batches = Watching(["ended"], {"msgbatch_new": [succeeded("job-0", '{"is_it_job": false}')]})
    client = SimpleNamespace(messages=SimpleNamespace(batches=batches))

    extract.run_batch(client, [one], extract.MODEL, {}, poll=60)

    assert seen["batch_id"] == "msgbatch_new"
    assert seen["key"] == extract.cache_key(one)
    assert not extract.PENDING_PATH.exists()
    assert extract.load_cache()[extract.cache_key(one)]["is_it_job"] is False


def test_open_batch_is_resumed_and_not_submitted_again(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(extract.time, "sleep", lambda _seconds: None)
    one = row("https://a")
    extract.save_pending("msgbatch_old", extract.MODEL, [
        {"custom_id": "job-0", "key": extract.cache_key(one)},
    ])
    batches = Batches(
        ["in_progress", "ended"],
        {"msgbatch_old": [succeeded("job-0", '{"is_it_job": true}')]},
    )
    client = SimpleNamespace(messages=SimpleNamespace(batches=batches))

    extract.run_batch(client, [one], extract.MODEL, {}, poll=60)

    assert batches.created == []
    assert batches.retrieved == ["msgbatch_old", "msgbatch_old"]
    assert not extract.PENDING_PATH.exists()
    assert extract.load_cache()[extract.cache_key(one)]["is_it_job"] is True


def test_unparseable_batch_reply_stays_out_of_the_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(extract.time, "sleep", lambda _seconds: None)
    bad = SimpleNamespace(
        custom_id="job-0",
        result=SimpleNamespace(type="succeeded", message=text_message("{")),
    )
    batches = Batches(["ended"], {"msgbatch_new": [bad]})
    client = SimpleNamespace(messages=SimpleNamespace(batches=batches))
    cache = {}

    extract.run_batch(client, [row("https://a")], extract.MODEL, cache, poll=60)

    assert cache == {}
    assert not extract.CACHE_PATH.exists()
    assert not extract.PENDING_PATH.exists()


def test_missing_batch_is_submitted_again(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(extract.time, "sleep", lambda _seconds: None)
    one = row("https://a")
    extract.save_pending("msgbatch_old", extract.MODEL, [
        {"custom_id": "job-0", "key": extract.cache_key(one)},
    ])

    class Gone(Exception):
        status_code = 404

    batches = Batches(
        [Gone("missing"), "ended"],
        {"msgbatch_new": [succeeded("job-0", '{"is_it_job": true}')]},
    )
    client = SimpleNamespace(messages=SimpleNamespace(batches=batches))

    extract.run_batch(client, [one], extract.MODEL, {}, poll=60)

    assert len(batches.created) == 1
    assert batches.retrieved == ["msgbatch_old", "msgbatch_new"]
    assert extract.load_cache()[extract.cache_key(one)]["is_it_job"] is True


def test_changed_prompt_does_not_block_a_new_batch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(extract.time, "sleep", lambda _seconds: None)
    extract.PENDING_PATH.parent.mkdir(parents=True)
    extract.PENDING_PATH.write_text(json.dumps({
        "batch_id": "msgbatch_old",
        "model": extract.MODEL,
        "prompt_version": "gate-old",
        "items": [{"custom_id": "job-0", "key": "stale"}],
    }), encoding="utf-8")
    batches = Batches(["ended"], {"msgbatch_new": [succeeded("job-0", '{"is_it_job": true}')]})
    client = SimpleNamespace(messages=SimpleNamespace(batches=batches))

    extract.run_batch(client, [row("https://a")], extract.MODEL, {}, poll=60)

    assert "msgbatch_old" not in batches.retrieved
    assert len(batches.created) == 1
