import json, sys, collections, re
R = [json.loads(l) for l in open(sys.argv[1])]
M = ["s60", "s80", "s100", "s120"]
def cls(r):
    if not r["has_code"]: return "no_code:" + ("length" if r["finish"] == "length" else "stop")
    if r["rc"] == 0: return "ok"
    if r["rc"] == -9: return "timeout"
    if r["rc"] == 3: return "no_step"
    if r["rc"] == 4: return "mesh_err"
    return "exc:" + (r["err_type"] or "?")
print("n per model", {m: sum(r["model"] == m for r in R) for m in M})
for m in M:
    rs = [r for r in R if r["model"] == m]
    if not rs: continue
    c = collections.Counter(cls(r) for r in rs)
    print(f"\n{m} n={len(rs)} exec={c['ok']/len(rs):.3f} finish=length {sum(r['finish']=='length' for r in rs)/len(rs):.3f} "
          f"think_med={sorted(r['think_chars'] for r in rs)[len(rs)//2]} code_med={sorted(r['code_chars'] for r in rs)[len(rs)//2]}")
    print("  ", c.most_common(8))
    print("   by bench exec:", {b: round(sum(cls(r)=='ok' for r in rs if r['bench']==b)/max(1,sum(r['bench']==b for r in rs)),3) for b in ("c4","c2","fam","rp2")})
    errs = collections.Counter(re.sub(r"'[^']*'", "'X'", r["err_line"])[:90] for r in rs if r["rc"] not in (0, None))
    print("   top errors:", errs.most_common(6))
