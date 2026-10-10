#!/bin/bash
# v5 verifier (RL-candidate warm start) on the same real-bench candidates as the v3b study, GPU 7, after training ends.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export CUDA_VISIBLE_DEVICES=${VGPU:-7} OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11213000/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python); G=results/grpo_eval
until [ -f runs/v5-verifier-rl-warm/final/adapter_model.safetensors ]; do sleep 60; done
while pgrep -u $USER -f "train_sft_v1[4]" >/dev/null; do sleep 30; done
S=""; for m in e55ctl mix_t10_s120 guide_mb8b_s60 soup1_s20 mix_b32_s200 gt10_mb8_s60 mix_t10_s200 mix_b32_s120 mix_cont_s200 guide2b_s120; do S="$S $m=$G/real_$m.json"; done
$PY train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir results/selection --prefix v5preds_ --verifier runs/v5-verifier-rl-warm/final --verifier-run v5-verifier-rl-warm --batch 8 \
  $S k32_t10s120=results/selection/vin_k32.json > results/selection/vscore_v5.log 2>&1
echo "VSCORE V5 DONE $?"
