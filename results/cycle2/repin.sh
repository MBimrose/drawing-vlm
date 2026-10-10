#!/bin/bash
# repin a process tree (root pid + all descendants, all threads) to a CPU list.  repin.sh <root pid> <cpulist>
root=$1; cpus=$2
desc() { echo $1; for c in $(pgrep -P $1); do desc $c; done; }
n=0; for p in $(desc $root); do taskset -apc $cpus $p >/dev/null 2>&1 && n=$((n+1)); done; echo "repinned $n processes under $root -> $cpus"
