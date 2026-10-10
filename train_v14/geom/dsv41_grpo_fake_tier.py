"""Memory smoke for the GRPO trainer path: N rows from an existing think tier, reasoning padded to ~--chars characters,
reply = short notes + the code block, alternating advantages +-0.5.  python dsv41_grpo_fake_tier.py <src tar> <out dir> [n] [chars]"""
import io, os, sys, tarfile
src, out = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 4; chars = int(sys.argv[4]) if len(sys.argv) > 4 else 30000
os.makedirs(out, exist_ok=True)
rows = {}
with tarfile.open(src) as t:
    for m in t.getmembers():
        k, _, ext = m.name.partition(".")
        rows.setdefault(k, {})[ext] = t.extractfile(m).read()
keys = [k for k, r in rows.items() if "png" in r and "code.py" in r][:n]
def add(t, name, b):
    ti = tarfile.TarInfo(name); ti.size = len(b); t.addfile(ti, io.BytesIO(b))
with tarfile.open(os.path.join(out, "fake-00000.tar"), "w") as t:
    for i, k in enumerate(keys):
        r = rows[k]; think = (r.get("think.txt") or b"Plan.").decode()
        c = 3000 if i == 0 else chars   # row 0 short: --ckpt-check runs it without checkpointing too
        think = (think + "\n") * max(1, c // max(1, len(think)))
        code = r["code.py"].decode()
        add(t, k + ".png", r["png"]); add(t, k + ".code.py", code.encode()); add(t, k + ".think.txt", think.encode())
        add(t, k + ".reply.txt", ("Plan above.\n\n```python\n" + code + "\n```").encode())
        add(t, k + ".adv.txt", (b"0.5" if i % 2 == 0 else b"-0.5"))
print(len(keys), "rows ->", out)
