# Pull the design template out of each Claude Design screen bundle.
import base64
import gzip
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
src_dir = root / ".working" / "screens"
out_dir = root / ".working" / "screens-inner"
out_dir.mkdir(parents=True, exist_ok=True)


def decode_entry(entry: dict) -> bytes:
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    return raw


def template_html(doc: str) -> str:
    m = re.search(r'<script type="__bundler/template">(.*?)</script>', doc, re.S)
    if not m:
        raise SystemExit("no template")
    return json.loads(m.group(1))


def strip_font_faces(css: str) -> str:
    return re.sub(r"@font-face\s*\{[^{}]*\}", "", css)


lines = [
    "# Claude Design (1).html — nội dung thiết kế 15 màn",
    "",
    "Lấy từ thẻ `__bundler/template` của từng màn trong file xuất `(1).html`.",
    "Phần CSS đã bỏ `@font-face`. Đây là trích để chưng cất, không phải spine.",
    "",
]

for path in sorted(src_dir.glob("*.html")):
    shell = path.read_text(encoding="utf-8")
    page = template_html(shell)
    (out_dir / path.name).write_text(page, encoding="utf-8")
    styles = strip_font_faces("\n".join(re.findall(r"<style>(.*?)</style>", page, re.S)))
    styles = re.sub(r"\n{3,}", "\n\n", styles).strip()
    # Visible-ish strings: text between tags, skip style/script
    no_style = re.sub(r"<style>.*?</style>", "", page, flags=re.S)
    no_style = re.sub(r"<script>.*?</script>", "", no_style, flags=re.S)
    bits = [re.sub(r"\s+", " ", t).strip() for t in re.findall(r">([^<]+)<", no_style)]
    bits = [b for b in bits if b and b not in {"/", "|"}]
    # Logic script kept separately, truncated
    scripts = "\n".join(re.findall(r"<script>(.*?)</script>", page, re.S))
    lines.append(f"## {path.stem}")
    lines.append(f"- html: `.working/screens-inner/{path.name}` ({len(page)} bytes)")
    lines.append("")
    lines.append("### Chữ trên màn")
    lines.append("")
    for b in bits:
        lines.append(f"- {b}")
    lines.append("")
    lines.append("### CSS (không font-face)")
    lines.append("")
    lines.append("```css")
    lines.append(styles[:8000])
    lines.append("```")
    lines.append("")
    lines.append("### Script (rút)")
    lines.append("")
    lines.append("```js")
    lines.append(scripts[:7000])
    lines.append("```")
    lines.append("")
    print(path.name, "page", len(page), "bits", len(bits), "css", len(styles), "js", len(scripts))

dest = root / ".working" / "claude-design-extract.md"
dest.write_text("\n".join(lines), encoding="utf-8")
print("digest", dest.stat().st_size)
