#!/bin/bash
#SBATCH --job-name=am-rp-h200
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --gres=gpu:8
#SBATCH --mem=1000G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/pipeline/logs/%x-%j.out
# American-VLM visual repair on a campus-cluster H200 node (2026-10-28, the H200 nodes are free again): 8 Glimmer repairer
# servers (TP1, bf16 = 59 GB each) and NR chain runners on the same node, claiming blocks from the shared serv-19 claims
# dir like the serv-19 and ccc0442 runners (am_runner.sh unchanged; vr_serve bench-B args unchanged). The servers run
# the serv-05 setup through srv_exec.sh (mirror of /srv/scratch/bimrose2): repairer final, base Glimmer chat template,
# no reasoning parser, 2 images. Runner state lives in its own ROOT ($P/h<node>) so the shared Lustre dirs of
# the ccc0442 job are not touched; summary_am.py reads every out dir.
#   sbatch --nodelist=ccc0474 --export=ALL,NR=8,W=12 am_rp_cluster.sbatch
# MODEL=gemma (2026-10-28): the Gemma 4 column, blocks in ../pipeline_gemma, claims in serv-19 gmpipe/claims, the Gemma
# repairer (am-gemma4-rp3recipe final, repaired for vLLM by fix_gemma4_final.py into final_vllm) served as gmrp with
# gmrp.jinja (thinking pinned on, as its training rows) and max_soft_tokens 1120 as every Gemma eval.
#   sbatch --nodelist=ccc0451 --export=ALL,MODEL=gemma,NR=8,W=12 am_rp_cluster.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; IP=$DV/results/indist_pipeline; R=/srv/scratch/bimrose2
case ${MODEL:-glimmer} in
  glimmer) P=$DV/results/american_vlm/pipeline; MODEL_DIR=$R/amvlm/runs/am-glimmer-rp3recipe/final; SNAME=glrp
           TEMPLATE=$R/models/Muse-Glimmer-30B/chat_template.jinja; VX=""; CLAIMS=$R/glpipe/claims; NEED="rp g4";;
  gemma)   P=$DV/results/american_vlm/pipeline_gemma; MODEL_DIR=$R/amvlm/runs/am-gemma4-rp3recipe/final_vllm; SNAME=gmrp
           TEMPLATE=$R/american_vlm/templates/gmrp.jinja; VX="--mm-processor-kwargs {\\\"max_soft_tokens\\\":1120}"
           CLAIMS=$R/gmpipe/claims; NEED="rp g4";;
  # Nemotron (2026-10-29): the Nemotron repairer (am-nemo-rp3recipe final, finalized for vLLM by nemotron_finalize_ckpt.py)
  # as nmrp with nmrp.jinja (thinking pinned on, as its training rows), 2 TP4 servers (240 GB of bf16 weights)
  nemotron) P=$DV/results/american_vlm/pipeline_nemo; MODEL_DIR=$R/amvlm/runs/am-nemo-rp3recipe/final; SNAME=nmrp
           TEMPLATE=$R/american_vlm/templates/nmrp.jinja; VX=""; CLAIMS=$R/nmpipe/claims; NEED="rp nemo"; TPV=4;;
  # Glimmer GRPO + visual repair (2026-10-29): the same Glimmer repairer, starts from the gl1 step-180 K=8 vote
  glgrpo)  P=$DV/results/american_vlm/pipeline_glgrpo; MODEL_DIR=$R/amvlm/runs/am-glimmer-rp3recipe/final; SNAME=glrp
           TEMPLATE=$R/models/Muse-Glimmer-30B/chat_template.jinja; VX=""; CLAIMS=$R/glgpipe/claims; NEED="rp g4";;
  # Gemma GRPO + visual repair (2026-10-29): the Gemma repairer, starts from the gm1 step-40 K=8 vote (picked on real-144)
  gmgrpo)  P=$DV/results/american_vlm/pipeline_gmgrpo; MODEL_DIR=$R/amvlm/runs/am-gemma4-rp3recipe/final_vllm; SNAME=gmrp
           TEMPLATE=$R/american_vlm/templates/gmrp.jinja; VX="--mm-processor-kwargs {\\\"max_soft_tokens\\\":1120}"
           CLAIMS=$R/gmgpipe/claims; NEED="rp g4";;
  *) echo "unknown MODEL $MODEL"; exit 2;;
esac
B=/projects/illinois/eng/ece/wpk/bimrose2; M=$B/srvmirror; SX=$DV/train_v14/sbatch/srv_exec.sh
HT=h$(hostname -s | sed 's/^ccc0*//'); RT=$P/$HT; mkdir -p $RT/logs $P/logs
cd $RT; mkdir -p out done mine locks failed
ln -sfn $P/blocks blocks; ln -sfn $P/blocks.txt blocks.txt; ln -sfn $P/drop_empty_rounds.py drop_empty_rounds.py
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
H=wpk-serv-19.mechse.illinois.edu
for g in $NEED; do until [ -f $M/MIRROR_$g ]; do sleep 60; done; done   # mirror_srv.sbatch: image, CUDA, repairer, base template
if [ ${MODEL:-glimmer} = nemotron ]; then
  until [ -f $M/amvlm/runs/am-nemo-rp3recipe/final/FINALIZED_FROM_BASE ]; do sleep 300; done
fi
if [ ${MODEL:-glimmer} = gemma ]; then   # the repairer final as the Gemma FT's: buffers + base config for vLLM
  until [ -f $M/amvlm/runs/am-gemma4-rp3recipe/final/model.safetensors.index.json ]; do sleep 300; done
  [ -f $M/${MODEL_DIR#$R/}/config.json ] || bash $SX "$R/.venv_g4/bin/python $DV/train_v14/geom/fix_gemma4_final.py \
    $R/amvlm/runs/am-gemma4-rp3recipe/final $R/models/gemma-4-31B-it $MODEL_DIR" || { echo "fix_gemma4_final failed"; exit 1; }
fi
# --- runner environment, as am_chains_c442.sbatch
C2=/dev/shm/bimrose2/c2stage; D=/dev/shm/bimrose2/ipcode; mkdir -p $C2
( flock 8
  [ -x $C2/venv/bin/python ] && [ -x $C2/dw_venv/bin/python ] || {
    rsync -a --copy-links $DV/.venv/ $C2/venv/ & rsync -a --copy-links $DV/dw_venv/ $C2/dw_venv/ & wait; }
  [ -f $C2/step_to_drw/.STAGED ] || { rsync -a $DV/mech_step_to_drw/ $C2/step_to_drw/ && touch $C2/step_to_drw/.STAGED; }
) 8>/dev/shm/bimrose2/c2stage.lock
bash $IP/stage_code_shm.sh && bash $IP/stage_py_shm.sh || { echo "staging failed"; exit 1; }
if [ ! -f $D/bench_b/READY ]; then
  mkdir -p $D/bench_b && rsync -a -L $DV/results/bench_b/bench/eval_cache_v15.pkl $DV/results/bench_b/bench/gt_meshes_v15 $D/bench_b/ \
    && [ "$(ls $D/bench_b/gt_meshes_v15 | wc -l)" = 280 ] && touch $D/bench_b/READY || { echo "bench B staging failed"; exit 1; }
fi
echo "$(date) staged: $(du -sh $D | cut -f1)"
PIDS=(); SPIDS=()
cleanup() { for p in "${PIDS[@]}" "${SPIDS[@]}"; do kill -- -$p 2>/dev/null; done; }
trap cleanup EXIT
# --- 8 / TPV repairer servers (one per GPU by default)
TPV=${TPV:-1}; NSV=$((8 / TPV)); SV=$(seq 0 $((NSV - 1)))
export LOCAL_TMP=/tmp/bimrose2_srv_$SLURM_JOB_ID
export APPTAINERENV_CUDA_HOME=/software/cuda-13.0 APPTAINERENV_PREPEND_PATH=/software/cuda-13.0/bin APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=3600
for g in $SV; do
  port=$((8851 + g))
  APPTAINERENV_VLLM_PORT=$((29700 + 50 * g)) CUDA_VISIBLE_DEVICES=$(seq -s, $((g * TPV)) $((g * TPV + TPV - 1))) setsid bash $SX "vllm serve $MODEL_DIR --served-model-name $SNAME --host 127.0.0.1 --port $port \
    --tensor-parallel-size $TPV --trust-remote-code --gpu-memory-utilization 0.88 --max-model-len 16384 --max-num-seqs 256 \
    --limit-mm-per-prompt '{\"image\": 2, \"video\": 0}' --chat-template $TEMPLATE $VX" > $RT/logs/vllm_$port.log 2>&1 < /dev/null &
  SPIDS+=($!); sleep 5
done
# 240 x 30 s: the Nemotron repairer (240 GB) loads from Lustre at ~8 min per shard (2026-10-29: ~55 min for 6 shards)
up=0; for k in $(seq 1 240); do
  up=0; for g in $SV; do curl -s -m 5 http://127.0.0.1:$((8851 + g))/health >/dev/null && up=$((up + 1)); done
  [ $up = $NSV ] && break; sleep 30; done
echo "$(date) servers healthy: $up/$NSV"
[ $up -gt 0 ] || { echo "no repairer server came up"; tail -20 $RT/logs/vllm_8851.log; exit 1; }
for g in $SV; do curl -s -m 5 http://127.0.0.1:$((8851 + g))/health >/dev/null && echo "http://127.0.0.1:$((8851 + g))/v1"; done > $RT/urls_$HT.txt
cat > $RT/host.env <<EOF
ROOT=$RT; HT=$HT; PY=$D/venv/bin/python; RPY=$D/dw_venv/bin/python; SD=$C2/step_to_drw
BENCH_B=$D/bench_b; BENCH_FULL=$D/fullpool; VRS=$D/train_v14/geom/vr_serve.py; MODEL=$SNAME; CLAIMS_SSH=$H; CLAIMS_DIR=$CLAIMS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOF
FIRST=$(head -1 $RT/urls_$HT.txt)
for r in $(seq 1 ${NR:-8}); do
  setsid bash $DV/results/american_vlm/pipeline/am_runner.sh $RT/host.env $FIRST ${W:-12} j${SLURM_JOB_ID}r$r > $RT/logs/runner_${SLURM_JOB_ID}_r$r.log 2>&1 < /dev/null &
  PIDS+=($!); echo "$(date) runner $r pid $!"; sleep 15
done
while :; do
  alive=0; for p in "${PIDS[@]}"; do kill -0 $p 2>/dev/null && alive=1; done
  [ $alive = 0 ] && break; sleep 60
done
echo "AM CHAIN RUNNERS DONE $(date)"
