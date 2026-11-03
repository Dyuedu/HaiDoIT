import base64, gzip, json, pathlib, re

root = pathlib.Path(__file__).resolve().parents[1]
text = (root / ".working" / "screens" / "01.html").read_text(encoding="utf-8")
m = re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.S)
man = json.loads(m.group(1))
print("entries", len(man))
for key, entry in man.items():
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    mime = entry.get("mime")
    head = raw[:80]
    print(f"{key[:8]} mime={mime} compressed={entry.get('compressed')} bytes={len(raw)} head={head[:60]!r}")

# also template length
t = re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S)
print("template", len(t.group(1)) if t else None)
order = re.search(r'<script type="__bundler/page_order">(.*?)</script>', text, re.S)
print("order", order.group(1)[:400] if order else None)
