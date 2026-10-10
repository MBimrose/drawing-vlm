#!/usr/bin/env bash
# serv-19 side of the DeepSeek GRPO loop (2026-10-06). GPUs 4-7 ONLY; GPUs 0-3 / port 8000 = the hub's vanilla replica.
# Called over ssh by dsv41_grpo_loop.sh (serv-20). Every long job runs setsid/nohup and leaves a marker; the driver polls.
#   serve <model dir> <log>        start vLLM (TP4+EP, :8200, served name "pol"); pgid -> $G/serve.pgid
#   up                              exit 0 iff :8200 answers /v1/models
#   stop                            kill OUR server's process group (pgid file only), wait until GPUs 4-7 are empty
#   train <tier> <out> <prev|-> <log>   GRPO update (dsv41_grpo_train_serv19.sh), marker <out>/DONE or <out>/FAILED
#   merge <adapter> <merged dir> <log> [delta scale]  BF16-attention merge (merge_dsv41_lora.py --bf16) in the vLLM image (CPU),
#                                   marker <merged>/MERGED or <merged>.FAILED; scale 0 = base in the same layout (round-0 control)
#   gpus                            memory used on GPUs 4-7 (MiB)
set -uo pipefail
S=/srv/scratch/bimrose2; G=$S/grpo_ds; mkdir -p $G
BASE=$(ls -d /scratch/bimrose2/dsv41_flash/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1)
gpus() { nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$1>=4{print $2}' | tr '\n' ' '; echo; }
case $1 in
serve)
  M=$2; [ "$M" = base ] && M=$BASE
  cd $S; MAXLEN=${MAXLEN:-32768} setsid nohup bash $S/train_v14/serv19/dsv41_ft_serve_serv19.sh "$M" pol 8200 4,5,6,7 > "$3" 2>&1 < /dev/null &
  echo $! > $G/serve.pgid; echo "serve pgid $(cat $G/serve.pgid) model $M";;
up)
  curl -s -m 10 127.0.0.1:8200/v1/models | grep -q '"pol"';;
stop)
  if [ -s $G/serve.pgid ]; then P=$(cat $G/serve.pgid); kill -TERM -- -$P 2>/dev/null; fi
  for i in $(seq 1 60); do
    busy=$(gpus | awk '{n=0; for(i=1;i<=NF;i++) if ($i>2000) n++; print n}')
    [ "$busy" = 0 ] && { rm -f $G/serve.pgid; echo "GPUs 4-7 free"; exit 0; }
    [ $i = 20 ] && [ -s $G/serve.pgid ] && kill -KILL -- -$(cat $G/serve.pgid) 2>/dev/null
    sleep 5
  done
  echo "GPUs 4-7 still busy: $(gpus)"; exit 1;;
train)
  TIER=$2; OUT=$3; PREV=$4; [ "$PREV" = - ] && PREV=""; LOG=$5; mkdir -p $OUT
  setsid nohup bash -c "bash $S/train_v14/serv19/dsv41_grpo_train_serv19.sh '$TIER' '$OUT' '$PREV' > '$LOG' 2>&1 && test -s '$OUT/adapter_model.safetensors' && touch '$OUT/DONE' || touch '$OUT/FAILED'" > /dev/null 2>&1 < /dev/null &
  echo "train started";;
merge)
  AD=${2/#\/srv\/scratch/\/scratch}; OUTM=${3/#\/srv\/scratch/\/scratch}; LOG=$4; DELTA_SCALE=${5:-1}; rm -rf "$OUTM" "$OUTM.FAILED"   # container binds /scratch/bimrose2 only
  setsid nohup bash -c "cd /scratch/bimrose2/dsv41_flash && apptainer exec --cleanenv --env OMP_NUM_THREADS=8 --env MKL_NUM_THREADS=8 --bind /scratch/bimrose2:/scratch/bimrose2 dsv41-flash-v0909.sif python3 /scratch/bimrose2/train_v14/geom/merge_dsv41_lora.py --base $BASE --adapter '$AD' --out '$OUTM' --bf16 --delta-scale ${DELTA_SCALE:-1} > '$LOG' 2>&1 && touch '$OUTM/MERGED' || touch '$OUTM.FAILED'" > /dev/null 2>&1 < /dev/null &
  echo "merge started";;
gpus) gpus;;
*) echo "unknown $1"; exit 2;;
esac
