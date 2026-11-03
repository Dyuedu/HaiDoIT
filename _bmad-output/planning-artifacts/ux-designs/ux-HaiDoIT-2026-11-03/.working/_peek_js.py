import base64, gzip, json, pathlib, re

root = pathlib.Path(__file__).resolve().parents[1]
text = (root / ".working" / "screens" / "06.html").read_text(encoding="utf-8")
man = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.S).group(1))
template = re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1)
print("--- TEMPLATE head ---")
print(template[:1500])
print("--- TEMPLATE tail ---")
print(template[-800:])

for key, entry in man.items():
    if entry.get("mime") != "text/javascript":
        continue
    raw = gzip.decompress(base64.b64decode(entry["data"])) if entry.get("compressed") else base64.b64decode(entry["data"])
    doc = raw.decode("utf-8", errors="replace")
    if "dc-runtime" not in doc[:80] and "React" in doc[:40]:
        continue
    print("JS", key[:8], "len", len(doc))
    for needle in ["Hà Nội", "Cỡ mẫu", "PostgreSQL", "đã biết", "CI/CD", "Khác"]:
        print(" ", needle, doc.find(needle))
    # print a window around PostgreSQL
    i = doc.find("PostgreSQL")
    if i >= 0:
        print(doc[max(0, i - 200): i + 400])
