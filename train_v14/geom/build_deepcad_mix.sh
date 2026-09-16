#!/usr/bin/env bash
# Pack the DeepCAD tier (rft_deepcad_e55, written by write_rft_real.py on serv-20 and rsynced
# here) into shards and build e58's mix: re-packed base + union5 x5 + DeepCAD tier x R.
#   build_deepcad_mix.sh <tier_dir> [R]      R defaults so the tier is ~35% of RFT draws
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; PY=$DV/.venv/bin/python
TIER=${1:-$DV/rft_deepcad_e55}; BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards
[ -f $TIER/accepted-000.jsonl ] || { echo "no accepted rows in $TIER"; exit 1; }
[ -d $TIER/shards ] || $PY $DV/train_v14/geom/pack_rft_shards_dir.py $TIER $TIER/png | tail -2
nb=$(ls $BASE/rft-*.tar | wc -l); nu=$(ls $U5/rft-*.tar | wc -l); nt=$(ls $TIER/shards/rft-*.tar | wc -l)
# choose R so that R*nt / (nb + 5*nu + R*nt) ~= 0.35  ->  R = 0.35*(nb+5*nu) / (0.65*nt)
R=${2:-$(python3 -c "import math; print(max(1, round(0.35*($nb+5*$nu)/(0.65*$nt))))")}
bash $DV/train_v14/geom/build_rft_mix.sh $DV/rft_mix_u8_deepcad_dw423 $BASE $U5 5
i=$(ls $DV/rft_mix_u8_deepcad_dw423 | wc -l)
for r in $(seq 1 $R); do for f in $TIER/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/rft_mix_u8_deepcad_dw423/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
echo "rft_mix_u8_deepcad_dw423: $i shards = $nb base + $((5*nu)) union5 + $((R*nt)) deepcad (R=$R, tier share $(python3 -c "print(f'{($R*$nt)/$i:.0%}')"))"
echo "next: sbatch $DV/train_v14/sbatch/e58-rft-deepcad-dw423.sbatch"
