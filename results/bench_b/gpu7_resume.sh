#!/bin/bash
# Reordered GPU-7 queue (2026-10-10 00:16): finish qwenbase on the 144 bench (clients already running), then the four
# bench-B models first, qwenbase on bench B last.
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
for p in 2294009 2294010 2294011 2294012; do while kill -0 $p 2>/dev/null; do sleep 30; done; done
say "qwenbase real: $(grep -h DONE logs/bbgen_real_qwenbase.*.log | wc -l)/4 shards done"
touch bench_b/eval/GEN_DONE_real_qwenbase
kill -- -1845492 2>/dev/null; sleep 20
for i in $(seq 1 30); do curl -s -m 3 http://127.0.0.1:8460/health >/dev/null || break; sleep 5; done
for i in $(seq 1 40); do u=$(nvidia-smi -i 7 --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' '); [ "$u" -lt 2000 ] && break; sleep 15; done
say "GPU 7 at ${u} MiB; starting bench-B queue"
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final; QB=/srv/scratch/bimrose2/models/Qwen3.8-27B
JOBS="e55ctl|$E55|benchb|2400|16384
rft2_rl_s60|runs/merged_bb_rft2_rl_s60|benchb|2400|16384
rft1_rl2_s120|runs/merged_bb_rft1_rl2_s120|benchb|2400|16384
ent_t10_s120|runs/merged_bb_ent_t10_s120|benchb|2400|16384
qwenbase|$QB|benchb|16000|24576" bash bench_b/code/eval_gpu7.sh
