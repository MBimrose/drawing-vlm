"""Make an eval bench (eval_cache_v15.pkl + gt_meshes_v15 + manifest) from an H6b tier's accepted rows, so the
training parts themselves can be generated on (think-mode self-distillation).  tier_to_bench.py <tier dir> <out dir> <corpora...>"""
import json, os, pickle, shutil, sys
tier, out, corpora = sys.argv[1], sys.argv[2], sys.argv[3:]
croot = {os.path.basename(c): c for c in corpora}
os.makedirs(os.path.join(out, "gt_meshes_v15"), exist_ok=True); samples, man = {}, {}
for l in open(os.path.join(tier, "accepted-000.jsonl")):
    r = json.loads(l); u = r["key"]; C, k = u.split("__", 1); C = croot[C]
    samples[u] = {"png": open(os.path.join(tier, "png", u + ".png"), "rb").read(), "code": r["code"], "trace": ""}
    shutil.copy(os.path.join(C, "gt_meshes_v15", k + ".stl"), os.path.join(out, "gt_meshes_v15", u + ".stl"))
    man[u] = json.load(open(os.path.join(C, "manifest.json")))["parts"][k]
pickle.dump({"samples": samples, "pools": {"certified": sorted(samples)}, "source": "h6b train tier " + tier, "render_meta": {}},
            open(os.path.join(out, "eval_cache_v15.pkl"), "wb"))
json.dump({"parts": man}, open(os.path.join(out, "manifest.json"), "w")); print(out, len(samples), "parts")
