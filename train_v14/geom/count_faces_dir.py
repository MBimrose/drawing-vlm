"""Face count of every STEP in a directory (B-rep faces), keyed by file stem -> json. Used for bench B (step_mm/)."""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
def faces(p):
    from build123d import import_step
    try:
        return os.path.basename(p)[:-5], len(import_step(p).faces())
    except Exception:
        return os.path.basename(p)[:-5], None
if __name__ == "__main__":
    d, out = sys.argv[1], sys.argv[2]
    ps = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".step"))
    with ProcessPoolExecutor(16) as ex:
        r = dict(ex.map(faces, ps))
    json.dump(r, open(out, "w"), indent=1); print(len(r), "parts", sum(v is None for v in r.values()), "failed")
