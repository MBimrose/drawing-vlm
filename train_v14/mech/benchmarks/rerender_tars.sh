#!/usr/bin/env bash
# Driver for the draftwright-0.4.23 re-render of the training sheets on wpk-serv-19
# (RECIPE.md "Training sheets re-rendered with draftwright 0.4.23"). Every step is
# resumable; run the whole file or one step:   rerender_tars.sh [tars|eval|corpora|bench|pack|all]
#
# Prerequisites on serv-19 (all under /srv/scratch/bimrose2):
#   tars_v14/                      rsync of the cluster's step_to_drw/wds_dataset/tars_v14 (2,500 tars + sidecars, 59 GB)
#   data/exec_bad_keys_v14.txt     the loader's exec-bad blocklist (those keys are skipped, not counted as failures)
#   data/certified_tar_keys_v15.txt  manifest tar_keys of the 1,072 certified eval parts (always attempted)
#   data/eval_v15_dw423/{step_mm,variants.json}   gt_meshes_v15/<uuid>.step + {uuid: variant N} from sft_manifest_v1
#   mech_benchmarks/{rerender_tars.py,rerender_one.py,rerender_exec.py}   (this directory, scp'd)
#   mech_benchmarks/step_to_drw/draftwright_compose.py patched with draftwright_compose_scale_policy.patch
#   .venv (build123d 0.11.1, executes the training scripts) and dw_venv (draftwright 0.4.23 + _FONT_SIZE 5.25)
set -uo pipefail
cd /srv/scratch/bimrose2
PY=.venv/bin/python; M=mech_benchmarks; STEP=${1:-all}
run() { echo "$(date) [$1] $2"; }

if [ "$STEP" = tars ] || [ "$STEP" = all ]; then
  # 497k parts: exec (120 s) + forced-variant render (400 s) per part, one worker process per shard.
  $PY $M/rerender_tars.py tars --tars $PWD/tars_v14 --out $PWD/tars_v14_dw423 --workers 256 \
    --log logs/rerender_tars_dw423.jsonl --skip-keys data/exec_bad_keys_v14.txt \
    --keep-keys data/certified_tar_keys_v15.txt > logs/rerender_tars_dw423.log 2>&1
fi
if [ "$STEP" = eval ] || [ "$STEP" = all ]; then
  # certified eval sheets from the bundle's GT STEPs (228 of them do not execute under 0.11.1)
  E=$PWD/data/eval_v15_dw423
  $PY $M/rerender_tars.py dir --src $E/step_mm --out $E/render --variants $E/variants.json --workers 16 \
    --log logs/rerender_eval_v15_dw423.jsonl > logs/rerender_eval_v15_dw423.log 2>&1
fi
if [ "$STEP" = corpora ] || [ "$STEP" = all ]; then
  # real-part corpora (union5's PNG sources) -> <corpus>/render_dw423/png/<key>_v<N>.png
  for C in rft_corpus rft_corpus2 rft_corpus3; do
    $PY $M/rerender_tars.py dir --src $PWD/$M/$C/step_mm --out $PWD/$M/$C/render_dw423 --workers 32 \
      --log logs/rerender_${C}_dw423.jsonl
  done > logs/rerender_corpora_dw423.log 2>&1
fi
if [ "$STEP" = bench ] || [ "$STEP" = all ]; then
  # held-out 146-part bench under the same (permissive) policy: ext_bench_dw423_perm
  B=$M/ext_bench_dw423_perm; mkdir -p $B/logs
  for f in step_mm gt_meshes_v15 split.json manifest.json legacy_keys_v14.txt traces_v14.json; do [ -e $B/$f ] || cp -r $M/ext_bench_dw423/$f $B/; done
  $PY $M/rerender_tars.py dir --src $PWD/$B/step_mm --out $PWD/$B/render --workers 16 \
    --log logs/rerender_ext_bench_dw423_perm.jsonl > logs/rerender_ext_bench_dw423_perm.log 2>&1
  $PY $M/build_ext_eval_cache.py --bench $B --png-dir $B/render/png > $B/logs/cache.log 2>&1; tail -1 $B/logs/cache.log
fi
if [ "$STEP" = pack ] || [ "$STEP" = all ]; then
  # RFT tiers on the new sheets: strict90 base straight from the new tars, union5 from the corpora renders.
  DRAWING_VLM_TARS=$PWD/tars_v14_dw423 $PY train_v14/geom/pack_rft_shards.py $PWD/rft_strict90_all_dw423 > logs/pack_strict90_dw423.log 2>&1; tail -1 logs/pack_strict90_dw423.log
  U=rft_real_union5_dw423; mkdir -p $U/png; miss=0
  while read k; do f=$(ls $M/rft_corpus/render_dw423/png/${k}_v*.png $M/rft_corpus2/render_dw423/png/${k}_v*.png $M/rft_corpus3/render_dw423/png/${k}_v*.png 2>/dev/null | head -1)
    if [ -n "$f" ]; then ln -sf $PWD/$f $U/png/$k.png; else miss=$((miss+1)); echo $k >> $U/missing_png.txt; fi; done < $U/keys.txt
  echo "union5 png links: $(ls $U/png | wc -l), missing $miss"
  $PY train_v14/geom/pack_rft_shards_dir.py $PWD/$U $PWD/$U/png > logs/pack_union5_dw423.log 2>&1; tail -1 logs/pack_union5_dw423.log
fi
