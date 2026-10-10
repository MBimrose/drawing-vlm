#!/bin/bash
# serv-20: when rp4c2 LoRA training ends, merge it into rp3's weights (merge_grpo_lora.py, as the repairer-RL loop evals
# did) and push the merged model to the cluster (runs/rp4c2-merged) for the L40S repair chains.
cd /srv/scratch/bimrose2
until grep -q "TRAIN DONE" cycle2/logs/rp4c2.driver; do sleep 60; done
grep -q "TRAIN DONE 0" cycle2/logs/rp4c2.driver || { echo "rp4c2 training failed"; exit 1; }
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt runs/rp3-delta-e55/final \
  --adapter runs/rp4c2-lora-rp3/final --out runs/rp4c2-merged --model-base runs/rp3-delta-e55/final > cycle2/logs/merge_rp4c2.log 2>&1 \
  || { echo "merge failed"; tail -5 cycle2/logs/merge_rp4c2.log; exit 1; }
du -sh runs/rp4c2-merged
rsync -a runs/rp4c2-merged wpk-cc:/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/runs/ 2>/dev/null && echo "pushed via wpk-cc" || echo "push failed (pull from cluster instead)"
touch cycle2/rp4/MERGED_DONE; echo "AFTER RP4 DONE $(date)"
