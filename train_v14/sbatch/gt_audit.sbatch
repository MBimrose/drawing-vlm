#!/bin/bash
#SBATCH --job-name=gt-audit
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=90
#SBATCH --mem=250G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

# Executes every GT build123d script in tars_v14 (one worker per shard,
# resumable). Workers can be SEGFAULTED by OCC on poison samples — the
# retry loop restarts each shard until complete (the worker's inflight
# marker records the poison sample so retries make progress), and `exit 0`
# keeps xargs from aborting the sweep on signal-killed children.
# Ends by merging results into exec_bad_keys_v14.txt (training blocklist).
set -uo pipefail
VENVPY=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/.venv/bin/python
TARS=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/tars_v14
OUT=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_exec_audit
AUDIT=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/geom/audit_shard.py
mkdir -p "$OUT"

export VENVPY AUDIT OUT
ls "$TARS"/shard_*.tar | xargs -P 85 -I{} bash -c '
  s=$(basename "$1" .tar)
  want=$(tar -tf "$1" | grep -c "\.py$")
  for try in 1 2 3 4 5 6 7 8; do
    have=$(wc -l < "$OUT/$s.jsonl" 2>/dev/null || echo 0)
    [ "$have" -ge "$want" ] && break
    "$VENVPY" "$AUDIT" "$1" "$OUT/$s.jsonl" || true
  done
  exit 0
' _ {}

echo "AUDIT SWEEP DONE $(date -Is)"
"$VENVPY" - <<'EOF'
import glob, json, os
OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_exec_audit"
bad, ok, errs = [], 0, {}
for p in glob.glob(os.path.join(OUT, "*.jsonl")):
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r["ok"]:
            ok += 1
        else:
            bad.append(r["key"])
            e = r["err"].split(":")[0][:40]
            errs[e] = errs.get(e, 0) + 1
dst = os.path.join(os.path.dirname(OUT), "exec_bad_keys_v14.txt")
with open(dst + ".tmp", "w") as f:
    f.write("\n".join(sorted(set(bad))) + "\n")
os.replace(dst + ".tmp", dst)
print(f"[merge] ok={ok} bad={len(bad)} -> {dst}")
print("[merge] top errors:", sorted(errs.items(), key=lambda x: -x[1])[:8])
EOF
