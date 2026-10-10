"""Bench B (2026-10-10): a SECOND held-out real-parts bench (~280 parts), frozen before any model is evaluated on it.

Why a new source: CADBench is exhausted (all 12,000 STEP rows went into corpora 1-4 / the 144-part bench; see
build_realpool_v2.py). Bench B therefore goes back to the datasets CADBench itself sampled from:
  F = Fusion 360 Gallery segmentation s2.0.1 extended STEP (CADBench benchF ids are exactly these
      "<project>_<hash>_<n>" names; 42,912 bodies in 10,082 designs),
  A = ABC (NYU, STEP chunks of 10k models; CADBench benchA ids are "<8-digit id>_<hash>_step_<nnn>").
Construction = the 144-part bench's: prep_external_parts.py filter (1 solid, analytic faces only, 6..80 faces,
aspect <= 15, fill >= 0.05, longest edge -> 80 mm) -> draftwright 0.4.23 + font patch via render_isolated.sh
(render_ext.py/worker_v11 VLM_MODE=1, permissive scale policy, NO legacy fallback; failures recorded verbatim) ->
build_ext_eval_cache.py. Underdetermined sheets are kept (as in the 144 bench).

Subcommands (all CPU; run on ccc0442 via sbatch/cpu_run.sh, never on the login node):
  exclusions  used-id sets from every manifest/inventory + a token scan of every key list under --scan roots
  candidates  F/A source STEPs minus exclusions, text prefilter, one body per design/model, seeded sample -> chunk dirs
  select      near-duplicate signature check + face-count-stratified selection (render list with oversampling)
  finalize    final keys = top quota renderable sheets per stratum (rank order) -> self-contained bench dir + freeze
  leakcheck   hard error on any overlap of the frozen bench with the exclusion sets (round-2 prep_keys.py rule)
"""
import argparse, collections, glob, hashlib, json, os, random, re, shutil, sys, time

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
DATA = f"{DV}/train_v14/mech/benchmarks/data"
BENCH144 = f"{DATA}/ext_bench_dw423_perm"
SEED = 20261010

RX_F = re.compile(r"(?<![0-9A-Za-z])(\d{3,6}_[0-9a-f]{8})_\d{1,4}(?![0-9a-f])")      # Fusion body -> design
RX_ABC = re.compile(r"(?<![\d.])(00\d{6})(?![\d.])")                                        # ABC / DeepCAD model id
RX_HASH = re.compile(r"(?<!\d)00\d{6}_([0-9a-f]{24})(?![0-9a-f])")                                 # ABC Onshape hash
FREEFORM = (b"B_SPLINE_SURFACE", b"SURFACE_OF_REVOLUTION", b"SURFACE_OF_LINEAR_EXTRUSION", b"OFFSET_SURFACE")


def toks(text):
    return set(RX_F.findall(text)), set(RX_ABC.findall(text)), set(RX_HASH.findall(text))


def load_manifests():
    """every prepared real-part manifest in the project: CADBench corpora, both real benches, abccode, DeepCAD."""
    out = {}
    for m in sorted(glob.glob(f"{DATA}/*/manifest.json")) + [f"{DV}/deepcad/corpus_full/manifest.json"]:
        if "/bench_b" in m:
            continue
        try:
            out[m] = json.load(open(m)).get("parts", {})
        except Exception as e:
            print(f"[excl] unreadable {m}: {e}", flush=True)
    return out


def sig_of(st):
    b = sorted(st["bbox"]); mx = max(b[2], 1e-9)
    return (st["faces"], tuple(sorted(st.get("kinds", {}).items()))), (b[0] / mx, b[1] / mx), st["fill"]


def cmd_exclusions(a):
    os.makedirs(a.out, exist_ok=True)
    F, A, H = set(), set(), set(); src = {}
    def add(name, f, ab, h):
        F.update(f); A.update(ab); H.update(h); src[name] = {"fusion_designs": len(f), "abc_ids": len(ab), "abc_hashes": len(h)}
    # 1. manifests (also collect near-duplicate signatures)
    sigs = collections.defaultdict(list); nsig = 0
    for m, parts in load_manifests().items():
        t = toks("\n".join(parts)); add(os.path.relpath(m, DV), *t)
        for k, st in parts.items():
            if isinstance(st, dict) and "bbox" in st and "fill" in st and "faces" in st:
                s0, bb, fill = sig_of(st); sigs[repr(s0)].append([k, bb[0], bb[1], fill]); nsig += 1
    json.dump(sigs, open(f"{a.out}/used_signatures.json", "w"))
    # 2. CADBench inventory (all 18,000 rows, incl. rows no corpus kept) + held-out id list + full DeepCAD id list
    inv = json.load(open(f"{DV}/data/cadbench_inventory/rows.json"))
    fam = {"bench0F": "F", "bench1A": "E", "bench1B": "A", "bench0": "B", "bench2": "M", "bench3": "O"}
    add("data/cadbench_inventory/rows.json", *toks("\n".join(f"{r['file_id']}" for r in inv)))
    add("train_v14/mech/benchmarks/data/heldout_file_ids.txt", *toks(open(f"{DATA}/heldout_file_ids.txt").read()))
    if a.deepcad_ids:
        ids = {l.strip() for l in open(a.deepcad_ids) if l.strip()}
        A.update(ids); src["deepcad_full_ids (serv-19 deepcad/data/cad_json, 215k)"] = {"abc_ids": len(ids)}
    # 3. token scan of every key list / tier / bank / pool file under the scan roots
    skip_dirs = {"png", "step_mm", "gt_meshes_v15", "render", "src", "iso", "shards", "src_chunks", "__pycache__", "logs"}
    nfiles = 0; t0 = time.time()
    for root in a.scan:
        rf, ra, rh = set(), set(), set(); n = 0
        walk = [(os.path.dirname(root), [], [os.path.basename(root)])] if os.path.isfile(root) else os.walk(root)
        for dp, dns, fns in walk:
            dns[:] = [d for d in dns if d not in skip_dirs and not d.startswith("bench_b")]
            for fn in fns:
                if not fn.endswith((".json", ".jsonl", ".txt", ".tsv", ".csv", ".yaml", ".yml")):
                    continue
                p = os.path.join(dp, fn)
                try:
                    if os.path.getsize(p) > a.max_mb * 2**20:
                        src.setdefault("_skipped_large", []).append(p); continue
                    t = toks(open(p, errors="ignore").read())
                except Exception:
                    continue
                rf |= t[0]; ra |= t[1]; rh |= t[2]; n += 1
        add(f"scan:{os.path.relpath(root, DV) if root.startswith(DV) else root} ({n} files)", rf, ra, rh); nfiles += n
        print(f"[excl] scanned {root}: {n} files, {len(rf)} F designs, {len(ra)} ABC ids  {time.time()-t0:.0f}s", flush=True)
    for name, s in (("used_fusion_designs.txt", F), ("used_abc_ids.txt", A), ("used_abc_hashes.txt", H)):
        open(f"{a.out}/{name}", "w").write("\n".join(sorted(s)) + "\n")
    json.dump({"sources": src, "totals": {"fusion_designs": len(F), "abc_ids": len(A), "abc_hashes": len(H),
               "signatures": nsig, "scanned_files": nfiles}}, open(f"{a.out}/exclusion_sources.json", "w"), indent=1)
    print(f"[excl] F designs {len(F)}  ABC ids {len(A)}  hashes {len(H)}  signatures {nsig}", flush=True)


def prefilter(path, fmin, fmax):
    b = open(path, "rb").read()
    if any(x in b for x in FREEFORM):
        return "freeform"
    if b.count(b"MANIFOLD_SOLID_BREP") != 1 or b.count(b"BREP_WITH_VOIDS"):
        return "solids"
    nf = b.count(b"ADVANCED_FACE")
    return None if fmin <= nf <= fmax else "faces"


def cmd_candidates(a):
    excl = a.excl
    usedF = {l.strip() for l in open(f"{excl}/used_fusion_designs.txt") if l.strip()}
    usedA = {l.strip() for l in open(f"{excl}/used_abc_ids.txt") if l.strip()}
    usedH = {l.strip() for l in open(f"{excl}/used_abc_hashes.txt") if l.strip()}
    rng = random.Random(SEED); stats = collections.Counter(); picks = {}
    # Fusion: one body per design
    by_design = collections.defaultdict(list)
    for p in sorted(glob.glob(f"{a.fusion_dir}/*.stp") + glob.glob(f"{a.fusion_dir}/*.step")):
        fid = os.path.splitext(os.path.basename(p))[0]; m = re.match(r"^(\d+_[0-9a-f]{8})_\d+$", fid)
        if not m: stats["F_badname"] += 1; continue
        if m.group(1) in usedF: stats["F_excluded_design"] += 1; continue
        by_design[m.group(1)].append((fid, p))
    designs = sorted(by_design); rng.shuffle(designs)
    nf = 0
    for d in designs:
        if nf >= a.n_f: break
        bodies = by_design[d]; rng.shuffle(bodies)
        for fid, p in bodies:
            why = prefilter(p, a.f_faces[0], a.f_faces[1])
            stats[f"F_pre_{why or 'ok'}"] += 1
            if why is None:
                picks[f"F_{fid}_x"] = p; nf += 1; break
    stats["F_designs_available"] = len(designs)
    # ABC: one part per model id and per Onshape hash
    models = collections.defaultdict(list)
    for p in sorted(glob.glob(f"{a.abc_dir}/**/*.step", recursive=True)):
        fid = os.path.splitext(os.path.basename(p))[0]; m = re.match(r"^(\d{8})_([0-9a-f]{24})_step_\d+$", fid)
        if not m: stats["A_badname"] += 1; continue
        if m.group(1) in usedA: stats["A_excluded_id"] += 1; continue
        if m.group(2) in usedH: stats["A_excluded_hash"] += 1; continue
        models[m.group(1)].append((fid, p, m.group(2)))
    ids = sorted(models); rng.shuffle(ids); seen_h = set(); na = 0
    for i in ids:
        if na >= a.n_a: break
        parts = models[i]; rng.shuffle(parts)
        for fid, p, h in parts:
            if h in seen_h: stats["A_dup_hash"] += 1; break
            why = prefilter(p, a.a_faces[0], a.a_faces[1])
            stats[f"A_pre_{why or 'ok'}"] += 1
            if why is None:
                picks[f"A_{fid}_x"] = p; seen_h.add(h); na += 1; break
    stats["A_models_available"] = len(ids)
    # chunk dirs of symlinks for parallel prep (prep reads <dir>/*.step)
    keys = sorted(picks); os.makedirs(a.out, exist_ok=True)
    for i, k in enumerate(keys):
        d = f"{a.out}/src/{i // a.chunk:03d}"; os.makedirs(d, exist_ok=True)
        dst = f"{d}/{k}.step"
        if not os.path.lexists(dst): os.symlink(os.path.abspath(picks[k]), dst)
    stats["F_candidates"] = nf; stats["A_candidates"] = na
    json.dump({"seed": SEED, "stats": dict(stats), "f_faces": a.f_faces, "a_faces": a.a_faces, "keys": keys},
              open(f"{a.out}/candidates.json", "w"), indent=1)
    print("[cand]", json.dumps(dict(stats)), flush=True)


def bench144():
    import pickle
    m = json.load(open(f"{BENCH144}/manifest.json"))["parts"]
    c = pickle.load(open(f"{BENCH144}/eval_cache_v15.pkl", "rb"))
    ks = [k for k in c["pools"]["certified"] if os.path.exists(f"{BENCH144}/gt_meshes_v15/{k}.stl")]
    return {k: m[k] for k in ks}


def strata(ref):
    """per family: face-count quartile edges of the 144 bench and its counts per bin."""
    import numpy as np
    out = {}
    for f in "FA":
        fs = [v["faces"] for k, v in ref.items() if k[0] == f]
        e = [float(x) for x in np.percentile(fs, [25, 50, 75])]
        cnt = [sum(1 for x in fs if b(x, e) == i) for i in range(4)]
        out[f] = {"edges": e, "counts": cnt, "n": len(fs)}
    return out


def b(x, e):
    return 0 if x <= e[0] else 1 if x <= e[1] else 2 if x <= e[2] else 3


def near_dup(st, sigs, tol):
    s0, bb, fill = sig_of(st)
    for k, b0, b1, fl in sigs.get(repr(s0), []):
        if abs(b0 - bb[0]) <= tol and abs(b1 - bb[1]) <= tol and abs(fl - fill) <= tol:
            return k
    return None


def cmd_select(a):
    man = json.load(open(a.prep_manifest))["parts"]
    sigs = json.load(open(f"{a.excl}/used_signatures.json"))
    ref = bench144(); S = strata(ref); total = a.target
    tgt = {"F": round(total * S["F"]["n"] / (S["F"]["n"] + S["A"]["n"]))}; tgt["A"] = total - tgt["F"]
    quota = {}
    for f in "FA":   # largest-remainder apportionment of the family target over the 4 face bins
        raw = [tgt[f] * c / S[f]["n"] for c in S[f]["counts"]]; q = [int(x) for x in raw]
        for i in sorted(range(4), key=lambda i: raw[i] - q[i], reverse=True)[: tgt[f] - sum(q)]: q[i] += 1
        quota[f] = q
    rng = random.Random(SEED + 1); dropped = collections.Counter(); dup_of = {}; pool = collections.defaultdict(list)
    keys = sorted(man); rng.shuffle(keys)                 # the rank order: one seeded shuffle of all prepped parts
    own = collections.defaultdict(list)
    for k in keys:
        st = man[k]; f = k[0]
        d = near_dup(st, sigs, a.tol)
        if d: dropped["near_dup_used"] += 1; dup_of[k] = d; continue
        d = near_dup(st, own, a.tol)
        if d: dropped["near_dup_within"] += 1; dup_of[k] = d; continue
        s0, bb, fill = sig_of(st); own[repr(s0)].append([k, bb[0], bb[1], fill])
        lo = 37 if f == "A" else 8
        if st["faces"] < lo: dropped[f"{f}_faces_below_bench_min"] += 1; continue
        pool[(f, b(st["faces"], S[f]["edges"]))].append(k)
    render = []
    for f in "FA":
        for i in range(4):
            n = min(len(pool[(f, i)]), int(quota[f][i] * a.oversample) + 3)
            render += pool[(f, i)][:n]
            if len(pool[(f, i)]) < quota[f][i]: print(f"[select] WARNING stratum {f}{i}: {len(pool[(f, i)])} < quota {quota[f][i]}", flush=True)
    out = {"seed": SEED + 1, "target": tgt, "strata": S, "quota": quota, "tol": a.tol, "dropped": dict(dropped),
           "near_dup_of": dup_of, "pool_sizes": {f"{f}{i}": len(pool[(f, i)]) for f in "FA" for i in range(4)},
           "rank": {f"{f}{i}": pool[(f, i)] for f in "FA" for i in range(4)}, "render_list": render}
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"[select] target {tgt} quota {quota} pools {out['pool_sizes']} dropped {dict(dropped)} render {len(render)}", flush=True)


def cmd_finalize(a):
    import subprocess
    sel = json.load(open(a.select)); man = json.load(open(a.prep_manifest))["parts"]
    side = json.load(open(f"{a.render_dir}/renderers.json"))
    ok = {}
    sk = {}   # sidecar keys carry the sheet variant: <key>_v<n>
    for s_ in side:
        m = re.match(r"^(.+)_v\d+$", s_)
        if m: sk.setdefault(m.group(1), []).append(s_)
    fails = {}
    for k in sel["render_list"]:
        pngs = sorted(glob.glob(f"{a.render_dir}/png/{k}_v*.png"))
        rs = [side[s_] for s_ in sk.get(k, [])]
        if pngs and rs and all(r.get("renderer") == "draftwright" for r in rs): ok[k] = pngs
        else:   # verbose failure record: the renderer's own log for this part
            lp = f"{a.render_dir}/iso/{k}/log"
            fails[k] = {"pngs": len(pngs), "renderers": [r.get("renderer") for r in rs],
                        "log": open(lp, errors="ignore").read()[-6000:] if os.path.exists(lp) else "no log"}
    json.dump(fails, open(os.path.join(os.path.dirname(a.select), "render_failures.json"), "w"), indent=1)
    print(f"[final] renderable {len(ok)} / {len(sel['render_list'])}; failures -> render_failures.json", flush=True)
    final = []; short = {}
    for f in "FA":
        for i in range(4):
            got = [k for k in sel["rank"][f"{f}{i}"] if k in ok][: sel["quota"][f][i]]
            if len(got) < sel["quota"][f][i]: short[f"{f}{i}"] = sel["quota"][f][i] - len(got)
            final += got
    if short: print(f"[final] WARNING strata short of quota: {short}", flush=True)
    B = a.bench; os.makedirs(f"{B}/step_mm", exist_ok=True); os.makedirs(f"{B}/gt_meshes_v15", exist_ok=True)
    os.makedirs(f"{B}/render/png", exist_ok=True)
    parts = {}
    for k in final:
        st = dict(man[k]); st["family"] = k[0]; st["label"] = "x"; st["stratum"] = f"{k[0]}{b(st['faces'], sel['strata'][k[0]]['edges'])}"
        parts[k] = st
        shutil.copy2(f"{a.prep_dir}/step_mm/{k}.step", f"{B}/step_mm/{k}.step")
        shutil.copy2(f"{a.prep_dir}/gt_meshes_v15/{k}.stl", f"{B}/gt_meshes_v15/{k}.stl")
        for p in ok[k]: shutil.copy2(p, f"{B}/render/png/")
    json.dump({s_: side[s_] for k in final for s_ in sk[k]}, open(f"{B}/render/renderers.json", "w"), indent=1, sort_keys=True)
    full_man = json.load(open(a.prep_manifest))
    json.dump({"target_mm": 80, "max_faces": 80, "parts": parts, "renderer": full_man.get("renderer"),
               "source": "bench B: Fusion 360 Gallery s2.0.1 extended STEP + ABC STEP chunks (see results/bench_b/README.md)"},
              open(f"{B}/manifest.json", "w"), indent=1)
    r = subprocess.run([sys.executable, f"{DV}/train_v14/mech/benchmarks/build_ext_eval_cache.py", "--bench", B,
                        "--png-dir", f"{B}/render/png"], capture_output=True, text=True)
    print(r.stdout[-800:], r.stderr[-800:], flush=True)
    print(f"[final] {len(final)} parts: F {sum(k[0]=='F' for k in final)} A {sum(k[0]=='A' for k in final)}", flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""): h.update(blk)
    return h.hexdigest()


def cmd_leakcheck(a):
    import pickle
    B = a.bench; man = json.load(open(f"{B}/manifest.json"))["parts"]
    c = pickle.load(open(f"{B}/eval_cache_v15.pkl", "rb"))
    keys = [k for k in c["pools"]["certified"] if os.path.exists(f"{B}/gt_meshes_v15/{k}.stl")]
    usedF = {l.strip() for l in open(f"{a.excl}/used_fusion_designs.txt") if l.strip()}
    usedA = {l.strip() for l in open(f"{a.excl}/used_abc_ids.txt") if l.strip()}
    usedH = {l.strip() for l in open(f"{a.excl}/used_abc_hashes.txt") if l.strip()}
    sigs = json.load(open(f"{a.excl}/used_signatures.json"))
    bad = []
    for k in keys:
        f, ab, h = toks(k)
        if f & usedF or ab & usedA or h & usedH: bad.append(("id", k))
        d = near_dup(man[k], sigs, a.tol)
        if d: bad.append(("near_dup", k, d))
    designs = collections.Counter(next(iter(toks(k)[0] or toks(k)[1])) for k in keys)
    dup_in = [d for d, n in designs.items() if n > 1]
    if len(keys) < a.min_n:
        sys.exit(f"FATAL bench B has {len(keys)} parts (< {a.min_n})")
    if bad or dup_in:
        sys.exit(f"FATAL bench B leak: {bad[:10]} ({len(bad)}), repeated design/model {dup_in[:10]}")
    rep = {"n": len(keys), "F": sum(k[0] == "F" for k in keys), "A": sum(k[0] == "A" for k in keys),
           "checked": {"fusion_designs": len(usedF), "abc_ids": len(usedA), "abc_hashes": len(usedH),
                       "signatures": sum(len(v) for v in sigs.values())},
           "sha256": {"eval_cache_v15.pkl": sha(f"{B}/eval_cache_v15.pkl"), "manifest.json": sha(f"{B}/manifest.json")},
           "keys_sha256": hashlib.sha256("\n".join(sorted(keys)).encode()).hexdigest()}
    json.dump(rep, open(a.out, "w"), indent=1); print("[leak] CLEAN", json.dumps(rep), flush=True)


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("exclusions"); p.add_argument("--out", required=True); p.add_argument("--scan", nargs="*", default=[])
    p.add_argument("--deepcad-ids", default=""); p.add_argument("--max-mb", type=float, default=400)
    p = sp.add_parser("candidates"); p.add_argument("--excl", required=True); p.add_argument("--fusion-dir", required=True)
    p.add_argument("--abc-dir", required=True); p.add_argument("--out", required=True); p.add_argument("--n-f", type=int, default=1500)
    p.add_argument("--n-a", type=int, default=1500); p.add_argument("--f-faces", type=int, nargs=2, default=[8, 51])
    p.add_argument("--a-faces", type=int, nargs=2, default=[37, 80]); p.add_argument("--chunk", type=int, default=100)
    p = sp.add_parser("select"); p.add_argument("--prep-manifest", required=True); p.add_argument("--excl", required=True)
    p.add_argument("--out", required=True); p.add_argument("--target", type=int, default=280)
    p.add_argument("--oversample", type=float, default=1.3); p.add_argument("--tol", type=float, default=0.01)
    p = sp.add_parser("finalize"); p.add_argument("--select", required=True); p.add_argument("--prep-manifest", required=True)
    p.add_argument("--prep-dir", required=True); p.add_argument("--render-dir", required=True); p.add_argument("--bench", required=True)
    p = sp.add_parser("leakcheck"); p.add_argument("--bench", required=True); p.add_argument("--excl", required=True)
    p.add_argument("--out", required=True); p.add_argument("--tol", type=float, default=0.01)
    p.add_argument("--min-n", type=int, default=250)
    a = ap.parse_args()
    {"exclusions": cmd_exclusions, "candidates": cmd_candidates, "select": cmd_select, "finalize": cmd_finalize,
     "leakcheck": cmd_leakcheck}[a.cmd](a)


if __name__ == "__main__":
    main()
