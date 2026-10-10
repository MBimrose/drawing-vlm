#!/bin/bash
#SBATCH --job-name=rft1-resub
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# rft1_rl2 continuation (2026-10-08; NAME/ARGS env override): runs after host job 11182777 ends (afterany); resumes rft1_rl from its newest
# adapter in a fresh 2-GPU grpo_fast_cluster job (vLLM GPU 0 + trainer GPU 1), entropy target pinned to the original
# run's first-5-step mean so the floor does not drift. Excludes nodes carrying other grpo-fast jobs (its EXIT trap
# pkills every "vllm serve" of the user on the node).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; NAME=${NAME:-rft1_rl2}; ARGS=${ARGS:-train_v14/sbatch/arms/ovl_rft1_rl2.txt}; R=runs/grpo_v_$NAME
N=$(ls -d $R/adapter_step* 2>/dev/null | sed 's/.*adapter_step//' | sort -n | tail -1)
[ -n "$N" ] || { echo "no $NAME adapter"; exit 1; }
[ "$N" -ge 299 ] && { echo "$NAME already finished (step $N)"; exit 0; }
cp $R/round_log.jsonl $R/round_log_pre_s$N.jsonl
A=$DV/train_v14/sbatch/arms/fast_${NAME}_resume.txt
# entropy target: keep the one pinned in the args file (it must NOT be re-measured on resume)
echo "$NAME|$(sed -E "s#--adapter [^ ]+ --start-step [0-9]+#--adapter $R/adapter_step$N --start-step $N#" $ARGS) --save-every 10" > $A
cat $A
sbatch --gres=gpu:H200:2 --cpus-per-task=32 --mem=360G --exclude=ccc0441,ccc0451,ccc0474 \
  --export=ALL,ARMS_FILE=$A $DV/train_v14/sbatch/grpo_fast_cluster.sbatch
