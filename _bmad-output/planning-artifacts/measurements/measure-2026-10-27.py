import json, sys, re, collections, glob, os
D = sys.argv[1]
rows = []
for f in glob.glob(os.path.join(D, "*.jsonl")):
    for line in open(f, encoding="utf-8"):
        if line.strip(): rows.append(json.loads(line))
CITY = [("Hà Nội", r"hà nội|ha noi|hanoi"), ("TP. Hồ Chí Minh", r"hồ chí minh|ho chi minh|hcm|sài gòn|saigon"),
        ("Đà Nẵng", r"đà nẵng|da nang"), ("Hải Phòng", r"hải phòng|hai phong"), ("Cần Thơ", r"cần thơ|can tho"),
        ("Quy Nhơn", r"quy nhơn|quy nhon|bình định"), ("Nha Trang", r"nha trang|khánh hòa")]
def city(loc):
    l = (loc or "").lower()
    for n, p in CITY:
        if re.search(p, l): return n
    return None
ROLE = [("Bảo mật", r"secur|pentest|soc analyst|bảo mật"), ("DevOps/Cloud", r"devops|cloud|sre|site reliab|infra|platform eng|system admin|sysadmin"),
        ("Data/AI", r"\bdata\b|\bai\b|machine learning|\bml\b|scientist|analytics|\bbi\b|llm|computer vision|nlp"),
        ("Mobile", r"mobile|android|ios|flutter|react native"), ("Frontend", r"front[- ]?end|reactjs|react\.js|vue|angular|\bui\b"),
        ("Backend", r"back[- ]?end|full[- ]?stack|java|\.net|php|golang|node|python|ruby|c#|c\+\+|software eng|developer|lập trình")]
def role(t):
    t = (t or "").lower()
    for n, p in ROLE:
        if re.search(p, t): return n
    return None
for r in rows:
    r["_city"] = city(r.get("location")); r["_role"] = role(r.get("title"))
    r["_vnd"] = r.get("min_salary_vnd") is not None or r.get("max_salary_vnd") is not None
    r["_usd"] = (not r["_vnd"]) and (r.get("min_salary_usd") is not None or r.get("max_salary_usd") is not None)
    r["_skills"] = {s["canonical_name"] for s in r.get("skills", [])}
N = len(rows)
print("Tổng tin:", N)
print("Nguồn:", collections.Counter(r["external_source"] for r in rows))
print("Thành phố:", collections.Counter(r["_city"] for r in rows).most_common())
print("Location ngoài 7 TP (mẫu):", collections.Counter(r.get("location") for r in rows if not r["_city"]).most_common(8))
print("Vai trò:", collections.Counter(r["_role"] for r in rows).most_common())
print("Cấp:", collections.Counter(r.get("level") for r in rows).most_common())
print("Có lương VND:", sum(r["_vnd"] for r in rows), "| chỉ USD:", sum(r["_usd"] for r in rows), "| không lương:", N-sum(r["_vnd"] or r["_usd"] for r in rows))
print("Lương VND theo nguồn:", collections.Counter(r["external_source"] for r in rows if r["_vnd"]))
roles = ["Backend","Frontend","Data/AI","DevOps/Cloud","Mobile","Bảo mật"]
cities = [c for c,_ in CITY]
def cells(levels):
    out = {}
    for c in cities:
        for ro in roles:
            out[(c,ro)] = sum(1 for r in rows if r["_city"]==c and r["_role"]==ro and r.get("level") in levels and r["_vnd"])
    return out
for lv in (["Junior"], ["Fresher"], ["Intern","Fresher","Junior"], ["Intern","Fresher","Junior","Middle","Senior","Unknown"]):
    cc = cells(lv); ok = sum(v>=30 for v in cc.values())
    print(f"\nCấp {lv}: ô ≥30 tin có lương VND = {ok}/42")
    print("  " + " | ".join(f"{ro:>12}" for ro in roles))
    for c in cities: print(f"{c:>16} " + " | ".join(f"{cc[(c,ro)]:>12}" for ro in roles))
    nat = {ro: sum(cc[(c,ro)] for c in cities) for ro in roles}
    print("       Toàn quốc", nat)
# open-count per city (map numbers, all levels, no salary filter)
print("\nSố tin bản đồ (mọi cấp, không lọc lương):", {c: sum(1 for r in rows if r["_city"]==c) for c in cities})
# eligibility definitions
print("\nSố kỹ năng/tin: trung vị", sorted(len(r["_skills"]) for r in rows)[N//2], "| tin không kỹ năng:", sum(1 for r in rows if not r["_skills"]))
def count(S, mode, thr=None, pool=rows):
    n=0
    for r in pool:
        k=r["_skills"]
        if not k: continue
        if mode=="and": ok = S <= k
        elif mode=="subset": ok = k <= S
        else: ok = len(k & S)/len(k) >= thr
        n+=ok
    return n
pool = [r for r in rows if r.get("level") in ("Intern","Fresher","Junior","Unknown")]
for owned, add in [({"Python","SQL"},{"Docker"}), ({"Python","SQL"},{"Machine Learning"}), ({"PHP","MySQL","JavaScript"},{"Docker"}), ({"Java","Spring Boot","SQL"},{"Docker"})]:
    print(f"\nĐã có {sorted(owned)} + giả định {sorted(add)} (pool {len(pool)} tin Intern/Fresher/Junior/Unknown):")
    for mode,thr in [("and",None),("subset",None),("cov",0.5),("cov",0.34),("cov",0.25)]:
        b=count(owned,mode,thr,pool); a=count(owned|add,mode,thr,pool)
        print(f"  {mode}{'' if thr is None else ' ≥'+str(thr)}: trước {b} → sau {a} (Δ {a-b})")
print("\n=== Lương VND + USD đổi, 3 TP ===")
for r in rows: r["_sal"] = r["_vnd"] or r["_usd"]
c3 = ["Hà Nội","TP. Hồ Chí Minh","Đà Nẵng"]
print("Tin có lương theo cấp:", collections.Counter(r.get("level") for r in rows if r["_sal"]))
for lv in (["Fresher","Junior"], ["Intern","Fresher","Junior","Middle","Senior","Unknown"]):
    print("Cấp", lv)
    for c in c3 + ["Toàn quốc"]:
        print(f"  {c:>16}", {ro: sum(1 for r in rows if (c=="Toàn quốc" or r["_city"]==c) and r["_role"]==ro and r.get("level") in lv and r["_sal"]) for ro in roles})
pool3=[r for r in rows if r["_city"] in c3]
print("Tin trong 3 TP:", len(pool3), "/", N)
