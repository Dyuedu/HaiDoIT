# Unpack nested Claude Design bundles until the visible screen HTML is reached.
import base64
import gzip
import html
import json
import pathlib
import re
from html.parser import HTMLParser

root = pathlib.Path(__file__).resolve().parents[1]
screens = sorted((root / ".working" / "screens").glob("*.html"))


def manifest_of(text: str):
    m = re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def decode_entry(entry: dict) -> bytes:
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    return raw


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
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "tr", "br", "section", "button", "label"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        s = " ".join(data.split())
        if s and s not in ("Unpacking...",):
            self.parts.append(s)


def visible_text(doc: str) -> str:
    parser = TextExtractor()
    parser.feed(doc)
    body = "\n".join(parser.parts)
    body = re.sub(r"\n{3,}", "\n\n", body)
    # drop bundler chrome
    lines = []
    for line in body.splitlines():
        if "requires JavaScript" in line or line.startswith("Loading ") or line == "Unpacking...":
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def deepest_html(doc: str, depth: int = 0) -> str:
    man = manifest_of(doc)
    if not man or depth > 4:
        return doc
    html_entries = []
    for key, entry in man.items():
        mime = entry.get("mime", "")
        if not str(mime).startswith("text/html"):
            continue
        try:
            inner = decode_entry(entry).decode("utf-8")
        except Exception:
            continue
        html_entries.append(inner)
    if not html_entries:
        return doc
    # Prefer the entry whose visible text is longest (the real screen, not a shell).
    ranked = sorted(html_entries, key=lambda d: len(visible_text(d)), reverse=True)
    best = ranked[0]
    if len(visible_text(best)) < 80 and manifest_of(best):
        return deepest_html(best, depth + 1)
    # If the best still wraps another design page, go deeper when the child has more text.
    child_man = manifest_of(best)
    if child_man:
        deeper = deepest_html(best, depth + 1)
        if len(visible_text(deeper)) > len(visible_text(best)):
            return deeper
    return best


lines = [
    "# Claude Design (1).html — nội dung nhìn thấy của 15 màn",
    "",
    "Giải nén từ file xuất có đuôi `(1).html`. Đây là trích văn bản để chưng cất spine, không phải spine.",
    "",
]
out_dir = root / ".working" / "screens-inner"
out_dir.mkdir(parents=True, exist_ok=True)

for path in screens:
    shell = path.read_text(encoding="utf-8")
    title_m = re.search(r"<title>(.*?)</title>", shell, re.S)
    title = html.unescape(re.sub("<[^>]+>", "", title_m.group(1))).strip() if title_m else path.stem
    inner = deepest_html(shell)
    (out_dir / path.name).write_text(inner, encoding="utf-8")
    text = visible_text(inner)
    hexes = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}", inner)))
    # keep product-ish colors, drop pure gray noise later in the spine pass
    lines.append(f"## {path.stem}. {title}")
    lines.append(f"- file: `.working/screens-inner/{path.name}`")
    lines.append(f"- bytes: {len(inner)}")
    lines.append(f"- visible chars: {len(text)}")
    lines.append("- hex: " + ", ".join(hexes[:50]))
    lines.append("")
    lines.append(text[:6000])
    lines.append("")
    print(f"{path.name} inner={len(inner)} visible={len(text)} title={title[:60]}")

dest = root / ".working" / "claude-design-extract.md"
dest.write_text("\n".join(lines), encoding="utf-8")
print("digest", dest.stat().st_size)
