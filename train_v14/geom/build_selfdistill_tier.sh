#!/usr/bin/env bash
# Merge the per-corpus self-distillation passes into one tier, pack it, and build e57's mix.
# Run after both selfdistill_k32.sbatch jobs have written their tiers.
#
#   build_selfdistill_tier.sh [repeat]        (repeat = shard-level upweight, default 8)
#
# Inputs   rft_selfdistill_rft_corpus_dw423/, rft_selfdistill_rft_corpus2_dw423/
#            each: accepted-000.jsonl {key, iou, ok, think, code, sample}, png/<key>.png, stats.json
# Outputs  rft_selfdistill_all/{accepted-000.jsonl, png/, shards/}
#          rft_mix_u7_sd_dw423/  = rft_strict90_all_dw423b (re-packed base, 77 shards)
#                                + rft_real_union5_dw423 x5 + the new tier x<repeat>
#
# Only ACCEPTED rows (exec and IoU >= 0.8) are packed, and each keeps the think trace of the
# draw that produced it -- the model's own reasoning, which is the whole point of the tier
# (RECIPE "Self-distilled real-part tier"; contrast e56's borrowed base-model plans).
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
PY=$DV/.venv/bin/python
REP=${1:-8}
OUT=$DV/rft_selfdistill_all
SRC=("$DV/rft_selfdistill_rft_corpus_dw423" "$DV/rft_selfdistill_rft_corpus2_dw423")

for d in "${SRC[@]}"; do
  [ -f "$d/accepted-000.jsonl" ] || { echo "missing $d/accepted-000.jsonl -- has the pass finished?"; exit 1; }
done

rm -rf "$OUT"; mkdir -p "$OUT/png"
# de-duplicate on (key, code): a key can be accepted several times across draws, and the two
# corpora are disjoint, but a resumed shard can repeat a row.
$PY - "$OUT" "${SRC[@]}" <<'PY'
import json, os, sys
out, srcs = sys.argv[1], sys.argv[2:]
seen, rows, keys = set(), [], set()
for d in srcs:
    n = 0
    for line in open(os.path.join(d, "accepted-000.jsonl")):
        r = json.loads(line)
        sig = (r["key"], r["code"])
        if sig in seen:
            continue
        seen.add(sig); rows.append(r); keys.add(r["key"]); n += 1
    print(f"[merge] {os.path.basename(d)}: +{n} rows")
with open(os.path.join(out, "accepted-000.jsonl"), "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
n_think = sum(1 for r in rows if (r.get("think") or "").strip())
print(f"[merge] {len(rows)} accepted rows over {len(keys)} parts; {n_think} carry a think trace")
PY

for d in "${SRC[@]}"; do
  for f in "$d"/png/*.png; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$OUT/png/$(basename "$f")"; done
done
echo "[merge] $(ls "$OUT/png" | wc -l) sheets linked"

$PY $DV/train_v14/geom/pack_rft_shards_dir.py "$OUT" "$OUT/png" | tail -2

bash $DV/train_v14/geom/build_rft_mix.sh $DV/rft_mix_u7_sd_dw423 \
  $DV/rft_strict90_all_dw423b/shards $DV/rft_real_union5_dw423/shards 5
i=$(ls $DV/rft_mix_u7_sd_dw423 | wc -l)
for r in $(seq 1 "$REP"); do
  for f in "$OUT"/shards/rft-*.tar; do
    ln -s "$(readlink -f "$f")" "$DV/rft_mix_u7_sd_dw423/rft-$(printf %05d $i).tar"; i=$((i+1))
  done
done
echo "rft_mix_u7_sd_dw423: $i shards ($(ls -la $DV/rft_mix_u7_sd_dw423 | grep -c strict90) base, \
$(ls -la $DV/rft_mix_u7_sd_dw423 | grep -c union5) union5, $(ls -la $DV/rft_mix_u7_sd_dw423 | grep -c selfdistill) self-distilled)"
echo "next: sbatch $DV/train_v14/sbatch/e57-rft-real-sd-dw423.sbatch"
