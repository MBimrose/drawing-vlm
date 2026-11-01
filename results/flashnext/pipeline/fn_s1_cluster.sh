#!/bin/bash
# Flash-Next full pipeline (2026-10-22), cluster side of S1-FN: when serv-19 has the S1 blocks and servers (fnpipe/S1_READY),
# copy the S1 start files, block files and blocks.txt into this ROOT (claims are global on serv-19), then make sure ccc0442
# runners are working: a running fn-chains job moves on to the S1 blocks by itself; otherwise submit a new one on all four
# repairer ports. Login-node work only (rsync + sbatch).
#   setsid nohup bash fn_s1_cluster.sh > logs/s1_cluster.log 2>&1 < /dev/null &
set -uo pipefail
P=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/flashnext/pipeline; cd $P
H=wpk-serv-19.mechse.illinois.edu; R=/srv/scratch/bimrose2/fnpipe
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until timeout 60 ssh -o BatchMode=yes $H "test -f $R/S1_READY"; do sleep 300; done
rsync -a "$H:$R/starts_fnei_*" $P/ && rsync -a "$H:$R/blocks/fnS1_*" $P/blocks/ && rsync -a $H:$R/blocks.txt $P/blocks.txt.s19 \
  && mv $P/blocks.txt.s19 $P/blocks.txt || { say "sync failed"; exit 1; }
say "S1 blocks synced: $(grep -c '^fnS1_' blocks.txt) ($(ls blocks | grep -c '^fnS1_') files)"
for p in 8803 8804; do grep -qx $p ports.txt 2>/dev/null || echo $p >> ports.txt; done   # the running job tunnels to them
say "ports.txt: $(tr '\n' ' ' < ports.txt)"
if squeue -h -u bimrose2 -n fn-chains -t RUNNING | grep -q .; then
  say "fn-chains job running: its runners take the S1 blocks"
else
  J=$(sbatch --parsable --cpus-per-task=100 --mem=400G --export=ALL,NR=8,W=12,PORTS="8801 8802 8803 8804" fn_chains_c442.sbatch)
  say "submitted fn-chains $J (4 ports)"
fi
