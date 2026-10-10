#!/bin/bash
# Cycle-2 SFT mix (2026-10-09), round-1 recipe with one declared change. Round 1: tier 1,859 rows x 22 = 40,898 row-draws vs
# the 13 e55 replay shards (results/guide/rft1/mix/rft-00000..00012 = 10 dw423b base + 3 union5, 24,887 rows) -> tier ~62%
# of RFT draws, ~50% of all draws (rft_frac 0.8 / reasoning 0.1 / plain 0.1).
# Round 2 keeps the tier at ~50% of draws (tier row-draws ~40,898) but splits it: CADBench rows (corpora 1/2/4, incl. the
# carried round-1 rows) 2/3 and DeepCAD realpool2 rows 1/3, so the sketch+extrude DeepCAD idiom does not swamp the
# CADBench idiom (handoff "Real-part pool v2": DeepCAD as SFT was inert on the real bench, e58). Steps = ~2 epochs over the
# CADBench rows at global batch 16 (realpool2 rows then get ~1 epoch).
# Output: results/cycle2/tier2_{cad,rp2}/shards (packed), MIX_INFO "<N_cad> <R_cad> <N_rp2> <R_rp2> <steps>".
# The mix dir itself is assembled on serv-20 (assemble_mix2.sh) from cycle2/replay + these shards.
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; C=$DV/results/cycle2; T=$C/tier2
for s in cad rp2; do
  rm -rf $C/tier2_$s; mkdir -p $C/tier2_$s/png
  if [ $s = rp2 ]; then python3 -c "import json,sys;[sys.stdout.write(l) for l in open('$T/accepted-000.jsonl') if json.loads(l)['bench']=='rft_realpool_v2']" > $C/tier2_$s/accepted-000.jsonl
  else python3 -c "import json,sys;[sys.stdout.write(l) for l in open('$T/accepted-000.jsonl') if json.loads(l)['bench']!='rft_realpool_v2']" > $C/tier2_$s/accepted-000.jsonl; fi
  python3 -c "import json,os;[os.symlink('$T/png/'+json.loads(l)['key']+'.png','$C/tier2_$s/png/'+json.loads(l)['key']+'.png') for l in open('$C/tier2_$s/accepted-000.jsonl')]"
  python3 $DV/train_v14/geom/pack_rft_shards_dir.py $C/tier2_$s --per-shard 465
done
NC=$(wc -l < $C/tier2_cad/accepted-000.jsonl); NR=$(wc -l < $C/tier2_rp2/accepted-000.jsonl)
read RC RR STEPS FRAC < <(python3 -c "
nc,nr=$NC,$NR; rc=max(1,round(40898*(2/3 if nr else 1)/nc)); rr=max(1,round(40898/3/nr)) if nr else 0
t=nc*rc+nr*rr; fc=0.8*nc*rc/(t+24887); print(rc,rr,int(round(2*nc/fc/16)),round(0.8*t/(t+24887),3))")
echo "$NC $RC $NR $RR $STEPS" > $C/MIX_INFO
echo "CADBench rows $NC x $RC, realpool2 rows $NR x $RR; tier share of all draws $FRAC; steps (2 CADBench epochs) $STEPS"
