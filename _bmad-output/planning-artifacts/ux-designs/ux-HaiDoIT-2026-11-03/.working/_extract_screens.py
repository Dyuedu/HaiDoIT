# One-off extract of the Claude Design HTML gallery. Not a product artifact.
import base64
import gzip
import html
import json
import pathlib
import re
from html.parser import HTMLParser

root = pathlib.Path(__file__).resolve().parents[1]
src = next(root.glob("*(1).html"))
text = src.read_text(encoding="utf-8")
manifest = json.loads(
    re.search(
        r'<script type="__bundler/manifest">(.*?)</script>', text, re.S
    ).group(1)
)
order = json.loads(
    re.search(
        r'<script type="__bundler/page_order">(.*?)</script>', text, re.S
    ).group(1)
)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "tr", "br", "section", "button"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        s = data.strip()
        if s:
            self.parts.append(s)


out_dir = root / ".working" / "screens"
out_dir.mkdir(parents=True, exist_ok=True)
lines = [
    "# Claude Design (1).html — trich van ban 15 man",
    "",
    "Trich co hoc tu file xuat co duoi (1).html. Day khong phai spine.",
    "",
]
for i, pid in enumerate(order, 1):
    entry = manifest[pid]
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    doc = raw.decode("utf-8")
    (out_dir / f"{i:02d}.html").write_text(doc, encoding="utf-8")
    title_m = re.search(r"<title>(.*?)</title>", doc, re.S)
    title = html.unescape(re.sub("<[^>]+>", "", title_m.group(1))).strip() if title_m else ""
    h1 = [
        re.sub(r"\s+", " ", re.sub("<[^>]+>", "", html.unescape(x))).strip()
        for x in re.findall(r"<h1[^>]*>(.*?)</h1>", doc, re.S)
    ]
    parser = TextExtractor()
    parser.feed(doc)
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(parser.parts))
    hexes = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}", doc)))
    fonts = sorted(set(re.findall(r"font-family:[^;}{]+", doc)))[:8]
    lines.append(f"## {i:02d}. {title}")
    lines.append(f"- id: `{pid}`")
    lines.append(f"- file: `.working/screens/{i:02d}.html`")
    lines.append(f"- bytes: {len(doc)}")
    if h1:
        lines.append("- h1: " + " | ".join(h1))
    if fonts:
        lines.append("- fonts: " + " ; ".join(fonts))
    lines.append("- hex: " + ", ".join(hexes))
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    print(f"{i:02d} {title[:90]} bytes={len(doc)}")

dest = root / ".working" / "claude-design-extract.md"
dest.write_text("\n".join(lines), encoding="utf-8")
print("digest", dest.stat().st_size)
