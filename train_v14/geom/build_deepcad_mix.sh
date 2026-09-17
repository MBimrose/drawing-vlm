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
# R repeats when the tier is small; when even one copy exceeds the target share, take an evenly spaced
# subset of NS shards instead (the full pass yielded 139 shards / 277k samples, 58% at R=1).
NS=$(python3 -c "print(round(0.35*($nb+5*$nu)/0.65))")
if [ -n "${2:-}" ]; then R=$2; NS=$nt; elif [ $nt -le $NS ]; then R=$(python3 -c "print(max(1, round($NS/$nt)))"); NS=$nt; else R=1; fi
rm -rf $DV/rft_mix_u8_deepcad_dw423
bash $DV/train_v14/geom/build_rft_mix.sh $DV/rft_mix_u8_deepcad_dw423 $BASE $U5 5
i=$(ls $DV/rft_mix_u8_deepcad_dw423 | wc -l)
SEL=$(python3 -c "import sys; fs=sorted(sys.argv[1:]); n=$NS; idx=[round(k*(len(fs)-1)/max(1,n-1)) for k in range(n)] if n<len(fs) else range(len(fs)); print(' '.join(fs[j] for j in sorted(set(idx))))" $TIER/shards/rft-*.tar)
for r in $(seq 1 $R); do for f in $SEL; do ln -s "$(readlink -f "$f")" "$DV/rft_mix_u8_deepcad_dw423/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
nsel=$(echo $SEL | wc -w)
echo "rft_mix_u8_deepcad_dw423: $i shards = $nb base + $((5*nu)) union5 + $((R*nsel)) deepcad ($nsel of $nt tier shards x R=$R, tier share $(python3 -c "print(f'{($R*$nsel)/$i:.0%}')"))"
echo "next: sbatch $DV/train_v14/sbatch/e58-rft-deepcad-dw423.sbatch"
