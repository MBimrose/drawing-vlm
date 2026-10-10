#!/usr/bin/env bash
# Host-generic GPU side of the DeepSeek GRPO loop (2026-10-07; = dsv41_grpo_s19.sh with every host fact configurable,
# used by dsgrpo3 on serv-20 GPUs 0,1,2,7). Config: HCFG=<file> exporting GPUS PORT SIF BASE BUSY_MIB APPTAINER_TMPDIR.
#   serve <model dir> <log> | up | stop | train <tier> <out> <prev|-> <log> | merge <adapter> <merged> <log> [scale] | gpus
set -uo pipefail
[ -n "${HCFG:-}" ] && . "$HCFG"
GPUS=${GPUS:-4,5,6,7}; PORT=${PORT:-8200}; BUSY_MIB=${BUSY_MIB:-2000}
SIF=${SIF:-/scratch/bimrose2/dsv41_flash/dsv41-flash-v0909.sif}
BASE=${BASE:-$(ls -d /scratch/bimrose2/dsv41_flash/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1)}
S=/srv/scratch/bimrose2; G=$S/grpo_ds; mkdir -p $G; PG=$G/serve_$PORT.pgid
gpus() { nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' -v L=",$GPUS," 'index(L, ","$1",")>0{print $2}' | tr '\n' ' '; echo; }
case $1 in
serve)
  cd $S; SIF=$SIF MAXLEN=${MAXLEN:-65536} setsid nohup bash $S/train_v14/serv19/dsv41_ft_serve_serv19.sh "$2" pol $PORT $GPUS > "$3" 2>&1 < /dev/null &
  echo $! > $PG; echo "serve pgid $(cat $PG) model $2 gpus $GPUS port $PORT";;
up)
  curl -s -m 10 127.0.0.1:$PORT/v1/models | grep -q '"pol"';;
stop)
  if [ -s $PG ]; then P=$(cat $PG); kill -TERM -- -$P 2>/dev/null; fi
  for i in $(seq 1 60); do
    busy=$(gpus | awk -v B=$BUSY_MIB '{n=0; for(i=1;i<=NF;i++) if ($i>B) n++; print n}')
    [ "$busy" = 0 ] && { rm -f $PG; echo "GPUs $GPUS free"; exit 0; }
    [ $i = 20 ] && [ -s $PG ] && kill -KILL -- -$(cat $PG) 2>/dev/null
    sleep 5
  done
  echo "GPUs $GPUS still busy: $(gpus)"; exit 1;;
train)
  TIER=$2; OUT=$3; PREV=$4; [ "$PREV" = - ] && PREV=""; LOG=$5; mkdir -p $OUT
  setsid nohup bash -c "bash $S/train_v14/serv19/dsv41_grpo_train_serv19.sh '$TIER' '$OUT' '$PREV' > '$LOG' 2>&1 && test -s '$OUT/adapter_model.safetensors' && touch '$OUT/DONE' || touch '$OUT/FAILED'" > /dev/null 2>&1 < /dev/null &
  echo "train started";;
merge)
  AD=${2/#\/srv\/scratch/\/scratch}; OUTM=${3/#\/srv\/scratch/\/scratch}; LOG=$4; DS=${5:-1}; rm -rf "$OUTM" "$OUTM.FAILED"
  setsid nohup bash -c "apptainer exec --cleanenv --env OMP_NUM_THREADS=8 --env MKL_NUM_THREADS=8 --bind /scratch/bimrose2:/scratch/bimrose2 $SIF python3 /scratch/bimrose2/train_v14/geom/merge_dsv41_lora.py --base $BASE --adapter '$AD' --out '$OUTM' --bf16 --delta-scale $DS > '$LOG' 2>&1 && touch '$OUTM/MERGED' || touch '$OUTM.FAILED'" > /dev/null 2>&1 < /dev/null &
  echo "merge started";;
gpus) gpus;;
*) echo "unknown $1"; exit 2;;
esac
