#!/bin/bash
# serv-20 GPU 2: vLLM e55 + 4 rft2_rl adapters (LoRA), diag sampling + execution (12 workers, single-thread subprocesses)
cd /srv/scratch/bimrose2; D=cycle2/diag; mkdir -p $D
.venv/bin/python - <<'PY'
import random
random.seed(0)
B = [("c4", "fp/h6/rft_corpus4", "fp/h6/real4_hard_keys.txt"), ("c2", "mech_benchmarks/rft_corpus2_dw423", "fp/h6/c2_hard_keys.txt"),
     ("fam", "fp/h6/train_bench", "fp/h6/fam_hard_keys.txt"), ("rp2", "mech_benchmarks/rft_realpool_v2", "fp/h6/realpool2_hard_4500.txt")]
with open("cycle2/diag/keys.tsv", "w") as f:
    for tag, d, kf in B:
        ks = [l.strip() for l in open(kf) if l.strip()]
        for k in random.sample(ks, 30): f.write(f"{tag}\t{d}\t{k}\n")
PY
R=runs/grpo_v_rft2_rl
CUDA_VISIBLE_DEVICES=2 DP=1 SEQS=256 GMU=0.85 PORT=8470 NAME=e55 \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 4 --lora-modules s60=$PWD/$R/adapter_step60 s80=$PWD/$R/adapter_step80 s100=$PWD/$R/adapter_step100 s120=$PWD/$R/adapter_step120" \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > $D/vllm.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 120); do curl -s -m 5 http://127.0.0.1:8470/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; kill -- -$VPID; exit 1; }
nice -n 10 .venv/bin/python $D/diag_rl.py --models s60,s80,s100,s120 --keys $D/keys.tsv --base-url http://127.0.0.1:8470/v1 --out $D/diag.jsonl --k 4 --workers 12
kill -- -$VPID; echo "RUN DIAG DONE $(date)"
