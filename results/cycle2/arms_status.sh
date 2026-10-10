#!/bin/bash
timeout 60 ssh -o BatchMode=yes wpk-serv-20.mechse.illinois.edu 'cd /srv/scratch/bimrose2; date "+%H:%M"; python3 cycle2/arm_stat.py rft2_kl rft2_raw g2_guided g2_guided_raw e55_t2_rl ent_s2;
grep -h "\[guard\]" logs/grpo_v_rft2_kl.log logs/grpo_v_rft2_raw.log logs/grpo_v_g2_guided*.log logs/grpo_v_e55_t2_rl.log 2>/dev/null | tail -n 3;
tail -n 1 logs/grpo_autoeval.log; tr "\r" "\n" < cycle2/logs/sft_e55t2.log | grep -oE "[0-9]+/955 \[[^]]*\]" | tail -n 1; tail -n 2 cycle2/logs/after_e55t2.log'
