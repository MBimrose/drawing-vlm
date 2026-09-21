#!/usr/bin/env bash
# Run a CPU task on a compute node instead of the login node.
#
# 2026-09-21: the campus-cluster process-control policy kills anything on a login node that
# exceeds 30 min CPU / wall. Renders, eval-cache builds, mesh/IoU scoring, image work and any
# find/grep over the project tree must go through the scheduler. Login-node work is limited to
# editing, short greps in a known directory, sbatch/squeue and sleep-loop watchers.
#
#   bash train_v14/serv19/cpu_run.sh [-c CPUS] [-t TIME] [-m MEM] -- <command ...>
#
# Defaults: 8 cpus, 2 h, 64 G, wpk partition, the L40S nodes (ccc0442) — the GPU nodes are
# left for GPU jobs and ccc0441 carries someone else's long-running "test" job.
CPUS=8; TIME=02:00:00; MEM=64G; NODELIST=ccc0442
while [ $# -gt 0 ]; do
  case "$1" in
    -c) CPUS=$2; shift 2;;
    -t) TIME=$2; shift 2;;
    -m) MEM=$2; shift 2;;
    -n) NODELIST=$2; shift 2;;
    --) shift; break;;
    *) break;;
  esac
done
[ $# -gt 0 ] || { echo "usage: cpu_run.sh [-c CPUS] [-t TIME] [-m MEM] [-n NODELIST] -- <command>" >&2; exit 2; }
exec srun --account=wpk --partition=wpk --nodes=1 --ntasks=1 \
  --cpus-per-task="$CPUS" --mem="$MEM" --time="$TIME" --nodelist="$NODELIST" \
  --job-name=cpu-run --unbuffered bash -lc "cd /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm && $*"
