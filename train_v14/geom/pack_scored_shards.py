"""Pack verifier training data: every scored candidate from rft_generate
--log-all (scored-*.jsonl: key, sample, iou, exec, code) with its drawing
into scored-{train,eval}-NNNNNN.tar shards. Members <key>-s<j>.png /
.code.py / .meta.json({iou, exec}). Candidates without code are dropped;
execution failures are kept with iou=0 (the verifier must learn those).
2% of PARTS (hash of key) go to the eval shards.

    python pack_scored_shards.py <scored_dir> [<scored_dir2> ...]  -> <dir1>/shards
"""
import glob
import hashlib
import io
import json
import os
import sys
import tarfile

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
TARS = os.environ.get("DRAWING_VLM_TARS", f"{DV}/step_to_drw/wds_dataset/tars_v14")
DIRS = sys.argv[1:] or [f"{DV}/rft_scored_v1"]
OUT = os.environ.get("SCORED_OUT", os.path.join(DIRS[0], "shards"))
PER_SHARD = 4000
os.makedirs(OUT, exist_ok=True)

cands: dict[str, list] = {}
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(d, "scored-*.jsonl"))):
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not r.get("code"):
                continue
            lst = cands.setdefault(r["key"], [])
            if all(x["code"] != r["code"] for x in lst):
                lst.append(r)
print(f"[pack-scored] {sum(map(len, cands.values()))} candidates over {len(cands)} parts", flush=True)


def is_eval(key: str) -> bool:
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % 50 == 1


class Writer:
    def __init__(self, split):
        self.split, self.idx, self.n, self.tf, self.total = split, -1, 0, None, 0
        self._next()

    def _next(self):
        if self.tf:
            self.tf.close()
        self.idx += 1
        self.n = 0
        self.tf = tarfile.open(os.path.join(OUT, f"scored-{self.split}-{self.idx:06d}.tar"), "w")

    def add(self, name, data: bytes):
        ti = tarfile.TarInfo(name); ti.size = len(data)
        self.tf.addfile(ti, io.BytesIO(data))

    def sample(self, base, png, rec):
        self.add(f"{base}.png", png)
        self.add(f"{base}.code.py", rec["code"].encode())
        self.add(f"{base}.meta.json", json.dumps(
            {"iou": float(rec.get("iou", 0.0)), "exec": bool(rec.get("exec", False))}).encode())
        self.n += 1; self.total += 1
        if self.n >= PER_SHARD:
            self._next()


w = {"train": Writer("train"), "eval": Writer("eval")}
todo = set(cands)
for sp in sorted(glob.glob(os.path.join(TARS, "shard_*.tar"))):
    if not todo:
        break
    try:
        tf = tarfile.open(sp)
    except Exception:
        continue
    for n in tf.getnames():
        if n.endswith(".png") and n[:-4] in todo:
            key = n[:-4]
            try:
                png = tf.extractfile(n).read()
            except Exception:
                continue
            wr = w["eval" if is_eval(key) else "train"]
            for r in cands[key]:
                wr.sample(f"{key}-s{r.get('sample', 0)}", png, r)
            todo.discard(key)
    tf.close()
for x in w.values():
    x.tf.close()
print(f"[pack-scored] DONE train={w['train'].total} eval={w['eval'].total} unfound parts={len(todo)} -> {OUT}", flush=True)
