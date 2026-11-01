#!/bin/bash
# 2026-10-28 (user-approved): reverse ssh forward from an H200 node to serv-19 so serv-19 chain runners reach the node's
# repairer servers (serv-19 127.0.0.1:1885x -> node 127.0.0.1:885x). Re-dialled while the repair job <jobid> runs.
#   bash rtunnel_keep.sh <jobid>
J=$1; P=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/pipeline
F=(); for i in 1 2 3 4 5 6 7 8; do F+=(-R 1885$i:127.0.0.1:885$i); done
while [ ! -f $P/RELAY_STOP ] && squeue -h -j $J 2>/dev/null | grep -q .; do
  ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N "${F[@]}" wpk-serv-19.mechse.illinois.edu
  sleep 15
done
