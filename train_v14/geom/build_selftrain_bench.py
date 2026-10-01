"""Combined bench for DeepSeek self-training data (2026-09-30): real training corpora 1/2/4 parts where e55's best-of-K
is < 0.9 (where there is something to learn) + a sample of synthetic-family parts. Writes eval_cache_v15.pkl (pngs),
gt_meshes_v15/ symlinks, keys.txt (shuffled)."""
import json, os, pickle, random
B = "train_v14/mech/benchmarks/data"; OUT = "dsv41_selftrain_bench"
src = [("rft_corpus4", f"{B}/rft_corpus4/results/bo8_rft_corpus4_e55-rft-real-u5-gt-dw423.json"),
       ("rft_corpus_dw423", f"{B}/rft_corpus_dw423/results/bo32_rft_corpus_dw423_e55-rft-real-u5-gt-dw423.json"),
       ("rft_corpus2_dw423", f"{B}/rft_corpus2_dw423/results/bo32_rft_corpus2_dw423_e55-rft-real-u5-gt-dw423.json")]
os.makedirs(f"{OUT}/gt_meshes_v15", exist_ok=True); S = {}; keys = []; random.seed(0)
for c, bo in src:
    cache = pickle.load(open(f"{B}/{c}/eval_cache_v15.pkl", "rb"))["samples"]; n = 0
    for p in json.load(open(bo))["candidates"]:
        best = max([float(x.get("iou") or 0) for x in p["cands"]] or [0])
        k = p["key"]; g = os.path.realpath(f"{B}/{c}/gt_meshes_v15/{k}.stl")
        if best < 0.9 and k in cache and os.path.exists(g):
            S[k] = {"png": cache[k]["png"], "code": "", "trace": ""}; os.path.lexists(f"{OUT}/gt_meshes_v15/{k}.stl") or os.symlink(g, f"{OUT}/gt_meshes_v15/{k}.stl"); keys.append(k); n += 1
    print(c, n)
for c in ("family_scale1", "family_pilot"):
    cache = pickle.load(open(f"{B}/{c}/eval_cache_v15.pkl", "rb"))["samples"]; ks = sorted(cache); random.shuffle(ks); n = 0
    for k0 in ks[: 600 if c == "family_scale1" else 150]:
        k = f"{c}__{k0}"; g = os.path.realpath(f"{B}/{c}/gt_meshes_v15/{k0}.stl")
        if os.path.exists(g):
            S[k] = {"png": cache[k0]["png"], "code": cache[k0].get("code", ""), "trace": ""}; os.path.lexists(f"{OUT}/gt_meshes_v15/{k}.stl") or os.symlink(g, f"{OUT}/gt_meshes_v15/{k}.stl"); keys.append(k); n += 1
    print(c, n)
random.shuffle(keys)
pickle.dump({"samples": S, "pools": {"certified": keys}, "source": "dsv41 self-training", "render_meta": {}}, open(f"{OUT}/eval_cache_v15.pkl", "wb"))
open(f"{OUT}/keys.txt", "w").write("\n".join(keys) + "\n"); print("total", len(keys))
