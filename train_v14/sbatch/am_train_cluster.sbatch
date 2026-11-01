#!/bin/bash
#SBATCH --job-name=am-train-h200
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --gres=gpu:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/%x-%j.out
# American-VLM training on a campus-cluster H200 node (2026-10-28): serv19/am_train.sh (20-step smoke, then the run)
# unchanged inside srv_exec.sh, i.e. with the Lustre mirror at /srv/scratch/bimrose2 (mirror_srv.sbatch). Waits for the
# mirror groups in NEED, then copies the run's config (+ its accelerate file) from this repo into the mirror's code dir.
#   sbatch --nodelist=ccc0451 --export=ALL,CFG=am-gemma4-lora-e55recipe,VENV=.venv_g4,NEED="g4" am_train_cluster.sbatch
#   ENVX="DRAWING_VLM_RFT_SHARDS=/srv/scratch/bimrose2/rft_mix_rp3" (exported inside the container) for the repairers;
#   NGPU=4 (with --gres=gpu:4) for 4-rank configs; STAGE=1 stages the model on node-local disk
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; M=/projects/illinois/eng/ece/wpk/bimrose2/srvmirror
CFG=${CFG:?}; VENV=${VENV:-.venv_g4}
for g in ${NEED:-g4}; do until [ -f $M/MIRROR_$g ]; do sleep 60; done; done
C=$DV/train_v14/configs/$CFG.yaml; A=$(sed -n 's/^accel_config: *//p' $C)
cp $C $M/amvlm/train_v14/configs/ && cp $DV/train_v14/configs/$A $M/amvlm/train_v14/configs/
mkdir -p $M/amvlm/logs
# STAGE=1: copy model_id to node-local disk first (Lustre reads by every rank were ~8 s/tensor for Nemotron's 1,157)
if [ "${STAGE:-0}" = 1 ]; then
  MID=$(sed -n 's/^model_id: *//p' $C); LOC=/tmp/bimrose2_models/$(basename $MID)
  mkdir -p $LOC; rsync -a $M/${MID#/srv/scratch/bimrose2/}/ $LOC/ && sed -i "s|^model_id: .*|model_id: $LOC|" $M/amvlm/train_v14/configs/$CFG.yaml
  echo "$(date) staged $MID -> $LOC ($(du -sh $LOC | cut -f1))"
fi
NG=${NGPU:-8}; GL=$(seq -s, 0 $((NG - 1)))
echo "$(date) $CFG on $(hostname -s) (venv $VENV, accel $A, GPUs $GL)"
export LOCAL_TMP=/tmp/bimrose2_srv_$SLURM_JOB_ID
CUDA_VISIBLE_DEVICES=$GL bash $DV/train_v14/sbatch/srv_exec.sh \
  "export TRAIN_VENV=/srv/scratch/bimrose2/$VENV HF_HOME=/srv/scratch/bimrose2/.cache/huggingface ${ENVX:-}; cd /srv/scratch/bimrose2; \
   CFG=$CFG GPUS=$GL bash amvlm/train_v14/serv19/am_train.sh > amvlm/logs/$CFG.log 2>&1"
echo "$(date) exit $?: $(tail -2 $M/amvlm/logs/$CFG.log)"
