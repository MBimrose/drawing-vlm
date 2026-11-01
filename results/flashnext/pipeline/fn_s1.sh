#!/bin/bash
# Flash-Next full pipeline (2026-10-22), S1-FN on serv-19 = the bench-B S1 protocol (results/bench_b/pipeline: gen_k16_b.sh,
# stage2_b.sh, driver_b.sbatch) with the Flash-Next EI policy and the Flash-Next repairer:
#   1. fnei (step picked on real-144 + synthetic, fn55/FNEI_BEST) K=16 = draw 0 greedy + 15 at T 0.7 / top_p 0.95, think,
#      2400 tok, on bench B + synthetic. The LoRA is hot-loaded on e59/final as in the checkpoint evals. Two TP2 servers on GPUs 0-3.
#   2. stage 2 (CPU): score_partials (exec 60 s, IoU 90 s), consistency_rerank (part-sharded, cons_shard.py), render_compare
#      --tol 3 --gt-check 5 + rc_metric2 v3; the v3b-EV verifier (sel_vscore.py, 27B e51 base; GPUs 0 / 1)
#   3. pg_make_starts.py (top-3 distinct by verifier + v3) -> blocks fnS1_{benchb,full}_c{1,2,3} appended to blocks.txt
#   4. two more Flash-Next repairer servers (TP2: GPUs 0,1 :8803 and 2,3 :8804), added to urls_s19.txt; the cluster side
#      (fn_s1_cluster.sh) adds their ports to ports.txt for the ccc0442 tunnels
#   setsid nohup bash /srv/scratch/bimrose2/fnpipe/fn_s1.sh > /srv/scratch/bimrose2/fnpipe/logs/s1.log 2>&1 < /dev/null &
set -uo pipefail
S=/srv/scratch/bimrose2; R=$S/fnpipe; O=$R/s1; cd $S; mkdir -p $O/logs
PY=$S/.venv/bin/python; RPY=$S/dw_venv/bin/python; SD=$S/mech_step_to_drw; G=$R/code/train_v14/geom
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
say() { echo "$(date '+%m-%d %H:%M') $*"; }
fail() { say "FAILED: $*"; touch $O/FAILED; exit 1; }
bench() { case $1 in benchb) echo $S/mech_benchmarks/bench_b;; full) echo $S/mech_benchmarks/fullpool_dw423;; esac; }
say "waiting for the EI round (fn55/EI_DONE) and the step pick (fn55/FNEI_BEST)"
until [ -f fn55/EI_DONE ] && [ -s fn55/FNEI_BEST ]; do sleep 120; done
BEST=$(tr -dc 0-9 < fn55/FNEI_BEST); AD=$(readlink -f runs/fn_grpo_fnei/adapter_step$BEST)
[ -f $AD/adapter_model.safetensors ] || fail "no adapter $AD"
say "S1-FN generator: fnei s$BEST ($AD)"

# 1. K=16 generation
if [ ! -f $O/GEN_DONE ]; then
  export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
  for spec in "0,1 8771" "2,3 8772"; do
    set -- $spec
    ( MODEL=runs/e59-flashnext-e55recipe/final NAME=fnpol GPUS=$1 TP=2 PORT=$2 SEQS=128 GMU=0.88 \
        VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 1 --disable-custom-all-reduce" \
        exec setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > $O/logs/vllm_gen_$2.log 2>&1 < /dev/null ) &
    echo $! > $O/vllm_gen_$2.pgid
  done
  for port in 8771 8772; do
    ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
    [ $ok = 1 ] || fail "gen server :$port never ready: $(tail -3 $O/logs/vllm_gen_$port.log)"
    r=$(curl -s -m 600 -X POST 127.0.0.1:$port/v1/load_lora_adapter -H "Content-Type: application/json" -d "{\"lora_name\": \"fnei\", \"lora_path\": \"$AD\"}")
    say "load fnei on :$port: ${r:0:120}"
  done
  for b in benchb full; do
    GP=(); for i in 0 1 2 3; do
      port=$([ $i -lt 2 ] && echo 8771 || echo 8772)
      OMP_NUM_THREADS=2 $PY $G/gen_openai_bo.py --bench $(bench $b) --base-url http://127.0.0.1:$port/v1 --model fnei --k 16 \
        --temperature 0.7 --max-tokens 2400 --shard $i --nshards 4 --workers 16 --timeout 3600 --out $O/${b}_k16_fnei \
        > $O/logs/gen_${b}.$i.log 2>&1 &
      GP+=($!); done; wait "${GP[@]}"
    nd=$(grep -h "DONE shard" $O/logs/gen_${b}.*.log | wc -l); say "gen $b: $nd/4 shards"
    [ $nd = 4 ] || fail "gen $b incomplete"
  done
  for port in 8771 8772; do kill -TERM -- -$(cat $O/vllm_gen_$port.pgid) 2>/dev/null; done; sleep 60
  touch $O/GEN_DONE
fi

# 2. stage 2
for b in benchb full; do
  B=$(bench $b); STEM=$O/${b}_k16_fnei
  [ -f $STEM.json ] || nice -n 5 $PY $G/score_partials.py --partials "$STEM.shard*.json.partial.json" --gt-dir $B/gt_meshes_v15 \
    --out $STEM.json --workers 48 --exec-timeout 60 --iou-timeout 90 > $STEM.score.log 2>&1 || fail "score $b"
  say "scored $b: $(tail -1 $STEM.score.log)"
done
VP=()
for b in benchb full; do
  B=$(bench $b); STEM=$O/${b}_k16_fnei; gpu=$([ $b = benchb ] && echo 0 || echo 1)
  [ -f $O/vpreds_k16_fnei_$b.json ] && continue
  ( CUDA_VISIBLE_DEVICES=$gpu OMP_NUM_THREADS=4 PYTHONPATH=cycle2/train_v14:cycle2/train_v14/geom DRAWING_VLM_ROOT=$S \
      $PY cycle2/train_v14/geom/sel_vscore.py --cache $B/eval_cache_v15.pkl --outdir $O --batch 8 \
      --verifier runs/v3b-verifier-real-reg/final --base $S/runs/e51-rft-real-u3-strict90/final k16_fnei_$b=$STEM.json \
      > $O/logs/vscore_$b.log 2>&1; say "verifier $b exit $?" ) &
  VP+=($!)
done
CP=()
for b in benchb full; do
  STEM=$O/${b}_k16_fnei; N=$([ $b = benchb ] && echo 4 || echo 12); D=$O/cons_$b
  [ -f ${STEM}_consistency.json ] && continue
  ( python3 $R/cons_shard.py split $STEM.json $D $N > /dev/null
    P=(); for i in $(seq 0 $((N - 1))); do
      nice -n 5 $PY $G/consistency_rerank.py $D/shard_$i.json $D/shard_${i}_consistency.json > $D/shard_$i.log 2>&1 & P+=($!); done
    f=0; for p in "${P[@]}"; do wait $p || f=1; done
    [ $f = 0 ] && python3 $R/cons_shard.py merge $STEM.json $D $N ${STEM}_consistency.json && say "consistency $b merged" \
      || say "consistency $b FAILED" ) &
  CP+=($!)
done
for b in benchb full; do
  B=$(bench $b); STEM=$O/${b}_k16_fnei; mkdir -p ${STEM}_rcpng
  [ -f ${STEM}_rc.json ] || nice -n 5 $PY $G/render_compare.py --bo $STEM.json --bench $B --out ${STEM}_rc.json --py $PY --rpy $RPY \
    --script-dir $SD --workers 48 --tol 3 --gt-check 5 --save-png-dir ${STEM}_rcpng > ${STEM}_rc.log 2>&1
  [ -f ${STEM}_rc_v3.json ] || nice -n 5 $PY $G/rc_metric2.py --rc ${STEM}_rc.json --png-dir ${STEM}_rcpng --bench $B \
    --out ${STEM}_rc_v3.json --workers 48 > ${STEM}_rc_v3.log 2>&1
  say "render + v3 $b: $(tail -1 ${STEM}_rc_v3.log)"
done
for p in "${CP[@]}" "${VP[@]}"; do wait $p; done

# 3. starts + blocks
for b in benchb full; do
  STEM=$O/${b}_k16_fnei
  for f in ${STEM}_consistency.json $O/vpreds_k16_fnei_$b.json ${STEM}_rc_v3.json; do [ -s $f ] || fail "missing $f"; done
  $PY $G/pg_make_starts.py --cands $STEM.json --cons ${STEM}_consistency.json --vpreds $O/vpreds_k16_fnei_$b.json \
    --rc ${STEM}_rc_v3.json --out-stem $R/starts_fnei_$b --k 16 | tee -a $O/logs/starts.log || fail "starts $b"
done
cd $R
for b in benchb full; do for c in 1 2 3; do
  python3 make_blocks.py starts_fnei_${b}_r$c.json fnS1_${b}_c$c --b 24
  ls blocks | grep "^fnS1_${b}_c$c\.b" | sed 's/\.json$//' | sort >> blocks.txt
done; done
cd $S
say "S1 blocks appended: $(grep -c '^fnS1_' $R/blocks.txt)"

# 4. two more repairer servers on GPUs 0-3
M=$S/runs/fnrp-flashnext-rp3recipe/final
for spec in "0,1 8803" "2,3 8804"; do
  set -- $spec
  ( MODEL=$M NAME=fnrp GPUS=$1 TP=2 PORT=$2 SEQS=256 GMU=0.88 \
      VLLM_EXTRA='--limit-mm-per-prompt {"image":2,"video":0} --disable-custom-all-reduce' \
      exec setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > $R/logs/vllm_fnrp_$2.log 2>&1 < /dev/null ) &
  echo $! > $R/vllm_$2.pgid
done
for port in 8803 8804; do
  ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || fail "repairer server :$port never ready"
done
# the runners never exit while blocks remain (they poll), re-read blocks.txt every loop and pick a server per block from
# urls_s19.txt, so the S2 runners move on to the S1 blocks and start using the new servers by themselves
printf 'http://127.0.0.1:8801/v1\nhttp://127.0.0.1:8802/v1\nhttp://127.0.0.1:8803/v1\nhttp://127.0.0.1:8804/v1\n' > $R/urls_s19.txt
touch $R/S1_READY
say "S1 READY (servers :8801-:8804, $(pgrep -u bimrose2 -f "[f]n_runner.sh $R/host_s19.env" | wc -l) serv-19 runners)"
