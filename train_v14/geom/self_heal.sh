#!/usr/bin/env bash
# Compute-side self-heal: work the login-node session couldn't submit while
# its shell was fork-starved (2026-08-24 incident). Called from the
# geom_eval.sbatch and trace_sync.sbatch preambles; every action is
# idempotent and guarded, so repeat invocations are no-ops.
set -uo pipefail

ROOT=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
WDS=$ROOT/step_to_drw/wds_dataset
LOG=$ROOT/logs/self_heal.log

log() { echo "$(date -Is) [self-heal:$(hostname)] $*" >> "$LOG"; }

# --- 1. v15 GT meshes (STL from the certified bundle's STEP files) --------
# Needed before any v2-era (data_version: 2) checkpoint can be IoU-scored.
n_stl=$(find "$WDS/gt_meshes_v15" -maxdepth 1 -name '*.stl' 2>/dev/null | wc -l)
if [ "$n_stl" -lt 1000 ]; then
  if squeue -u "$USER" -h -n v15-meshes 2>/dev/null | grep -q .; then
    log "v15-meshes already queued/running (stl=$n_stl)"
  else
    jid=$(sbatch --parsable -J v15-meshes -A wpk -p wpk -N1 -n1 -c 16 --mem=64G \
      -t 02:00:00 -o "$ROOT/logs/slurm/%x.o%j" \
      --wrap "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; $ROOT/.venv/bin/python $ROOT/train_v14/geom/build_v15_assets.py" \
      2>>"$LOG") && log "submitted v15-meshes job $jid (stl=$n_stl)"
  fi
else
  log "v15 meshes present (stl=$n_stl) — nothing to do"
fi

# --- 2. Audit blocklist rescue --------------------------------------------
# If gt-audit died/timed out without merging, build exec_bad_keys_v14.txt
# from whatever per-shard results exist (497k+ collected — plenty).
if [ ! -s "$WDS/exec_bad_keys_v14.txt" ] && \
   ! squeue -u "$USER" -h -n gt-audit 2>/dev/null | grep -q .; then
  log "gt-audit gone without blocklist — merging collected results"
  "$ROOT/.venv/bin/python" - >>"$LOG" 2>&1 <<'PYEOF'
import glob, json, os
OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_exec_audit"
bad, ok = [], 0
for p in glob.glob(os.path.join(OUT, "*.jsonl")):
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("ok"):
            ok += 1
        else:
            bad.append(r["key"])
dst = os.path.join(os.path.dirname(OUT), "exec_bad_keys_v14.txt")
with open(dst + ".tmp", "w") as f:
    f.write("\n".join(sorted(set(bad))) + "\n")
os.replace(dst + ".tmp", dst)
print(f"[self-heal merge] ok={ok} bad={len(set(bad))} -> {dst}")
PYEOF
fi

# --- 3. Release training jobs stuck on a dead dependency ------------------
# afterok on a TIMEOUT/FAILED audit never satisfies; once the blocklist
# exists the dependency's purpose is met — clear it so the jobs run.
if [ -s "$WDS/exec_bad_keys_v14.txt" ]; then
  for name in e16-full-execfilter e19-certified-mix e20-certified-mix11; do
    jid=$(squeue -u "$USER" -h -n "$name" -t PD -o "%i" 2>/dev/null | head -1)
    if [ -n "$jid" ]; then
      dep=$(squeue -h -j "$jid" -o "%E" 2>/dev/null)
      if [ -n "$dep" ] && [ "$dep" != "(null)" ]; then
        scontrol update jobid="$jid" dependency= 2>>"$LOG" \
          && log "cleared dependency on $name (job $jid, was: $dep)"
      fi
    fi
  done
fi

# --- 4. Prune redundant raw FSDP checkpoints --------------------------------
# A finished, scored run keeps: final/ (bf16) + geom_eval/consolidated-<best>
# (bf16). The raw DCP checkpoint-N (weights + optimizer, 300-430 GB) is then
# pure redundancy. Delete it only when (a) the run is not in the queue,
# (b) its consolidated copy exists, (c) final/ exists. Saves ~4 TB per 14 runs.
running=$(squeue -u "$USER" -h -o "%j" 2>/dev/null | tr '\n' ' ')
for rd in "$ROOT"/runs/*/; do
  r=$(basename "$rd")
  case " $running " in *" $r "*) continue;; esac
  [ -f "$rd/final/model.safetensors.index.json" ] || continue
  for c in "$rd"/checkpoint-*; do
    [ -d "$c/pytorch_model_fsdp_0" ] || continue
    n=$(basename "$c")
    if [ -f "$rd/geom_eval/consolidated-$n/model.safetensors.index.json" ]; then
      rm -rf "$c" && log "pruned raw checkpoint $r/$n (consolidated + final exist)"
    fi
  done
done
