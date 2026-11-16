"""FR-23 — lời dẫn và tên tài liệu của lộ trình giả (#212, sửa sau review).

Quét cả `blurb` và `resource.title` của mọi kỹ năng trong fixture, không chỉ những gì API trả. Lời dẫn nói kỹ năng
dùng để làm gì và vì sao quan trọng với vai trò, không nói có bao nhiêu tin đòi nó.
"""

import json
from pathlib import Path
from urllib.parse import urlparse

from haido_core.vocab.prepared_text import prepared_text_problems

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "haido_api"
    / "fixtures"
    / "fake_learning_path.json"
)
FREQUENCY_CLAIMS = (
    "phần lớn", "đa số", "phổ biến", "hay gặp", "thường gặp", "nhiều tin", "mọi tin", "hầu hết", "thường chạy",
)  # fmt: skip
RETIRED_HOSTS = {"restfulapi.net", "linuxjourney.com", "junit.org"}
RETIRED_PREFIXES = (  # tài liệu của một nhà cung cấp cho kỹ năng trung lập, và trang chủ chung chung
    "https://aws.amazon.com/getting-started",
    "https://docs.aws.amazon.com/glue/",
    "https://docs.aws.amazon.com/redshift/",
)


def _nodes() -> list[tuple[str, dict]]:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [
        (f"{role}.{n['skill']}", n)
        for role, entry in raw["roles"].items()
        for n in entry["skills"]
    ]


def test_fr23_blurb_va_tieu_de_tai_nguyen_khong_co_so_ngoai_ten_cong_nghe_khong_phan_tram() -> (
    None
):
    nodes = _nodes()
    assert len(nodes) >= 20
    for key, node in nodes:
        for field, text in (
            ("blurb", node["blurb"]),
            ("resource.title", node["resource"]["title"]),
        ):
            assert text.strip(), f"{key}.{field} rỗng"
            assert prepared_text_problems(text) == [], f"{key}.{field}: {text}"


def test_fr23_loi_dan_khong_noi_ve_tan_suat_trong_tin_tuyen_dung() -> None:
    for key, node in _nodes():
        text = node["blurb"].casefold()
        for phrase in FREQUENCY_CLAIMS:
            assert phrase not in text, (
                f"{key}: lời dẫn có cụm {phrase!r}: {node['blurb']}"
            )


def test_fr23_tai_nguyen_khong_dung_host_da_bo() -> None:
    for key, node in _nodes():
        host = urlparse(node["resource"]["url"]).hostname
        url = node["resource"]["url"]
        assert host not in RETIRED_HOSTS, f"{key}: {url}"
        assert not url.startswith(RETIRED_PREFIXES), f"{key}: {url}"
