#!/bin/bash
# Main-protocol eval of an American-VLM e55-recipe fine-tune (2026-10-27, results/american_vlm/README.md), serv-19.
# eval_nemo.sh (K=8: draw 0 greedy + 7 at T 0.7 / top_p 0.95, think, 2400 tokens, the e55 prompt) on real-144 /
# synthetic 1,027 / bench B, twice:
#   $TAG    plain generation prompt
#   ${TAG}pf  thought-prefilled (Nemotron learned to skip thinking on 22% of draws; untraced rows teach the same here):
#           glimmer "<|start|>assistant to=self<|message|>1."   gemma "<|turn>model\n<|channel>thought\n1."
# The prefill is a served chat template (an assistant-message prefill lands in Glimmer's answer channel).
# Four TP2 servers: plain GPUs 0,1 / 2,3, prefill 4,5 / 6,7; per variant "real benchb" on one, "full" on the other.
# Waits for amvlm/logs/$RUN.TRAIN_DONE and $MODEL/config.json. Scoring: nemo_score.sbatch on ccc0442.
#   RUN=am-glimmer-30b-e55recipe TAG=glft KIND=glimmer setsid nohup bash amvlm/train_v14/serv19/am_eval_ft.sh \
#     > american_vlm/logs/eval_glft.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
RUN=${RUN:?}; TAG=${TAG:?}; KIND=${KIND:?}; MODEL=${MODEL:-/srv/scratch/bimrose2/amvlm/runs/$RUN/final}
O=american_vlm; T=$O/templates; mkdir -p $O/results $O/logs $T
case $KIND in
  glimmer) BASE=models/Muse-Glimmer-30B RPARSER=muse_glimmer EXTRA=""
           GEN="{{- '<|start|>assistant' -}}" PF="{{- '<|start|>assistant to=self<|message|>1.' -}}" ;;
  gemma)   BASE=models/gemma-4-31B-it RPARSER=gemma4 EXTRA='--mm-processor-kwargs {"max_soft_tokens":1120}'
           GEN="{{- '<|turn>model\n' -}}" PF="{{- '<|turn>model\n<|channel>thought\n1.' -}}" ;;
  *) echo "KIND glimmer|gemma"; exit 2 ;;
esac
until [ -f amvlm/logs/$RUN.TRAIN_DONE ] && [ -f $MODEL/config.json ]; do sleep 120; done
say "model ready: $MODEL"
cp $BASE/chat_template.jinja $T/${TAG}.jinja
GEN="$GEN" PF="$PF" .venv/bin/python - $T/${TAG}.jinja $T/${TAG}pf.jinja <<'EOF'
import os, sys
s = open(sys.argv[1]).read()
head, gen, tail = s.rpartition(os.environ["GEN"])   # the generation prompt is the template's last use of the line
assert gen and "add_generation_prompt" in head[-200:], "generation-prompt line not found"
open(sys.argv[2], "w").write(head + os.environ["PF"] + tail)
EOF
[ -s $T/${TAG}pf.jinja ] || { say "prefill template failed"; exit 1; }
diff $T/${TAG}.jinja $T/${TAG}pf.jinja
serve() {  # name gpus port template
  curl -s -m 5 http://127.0.0.1:$3/health > /dev/null && { say "reusing the server on :$3"; return; }
  MODEL=$MODEL NAME=$1 GPUS=$2 TP=2 PORT=$3 RPARSER=$RPARSER SEQS=128 GMU=0.85 \
    VLLM_EXTRA="--chat-template $PWD/$4 $EXTRA" \
    setsid nohup bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > $O/logs/vllm_$1_$3.log 2>&1 < /dev/null &
  echo $! > $O/vllm_$3.pgid
}
# PAIRS (2026-10-27): two GPU pairs -> one server per variant running all three benches (the rest of serv-19 is in GRPO)
PAIRS=(${PAIRS:-0,1 2,3 4,5 6,7})
if [ ${#PAIRS[@]} = 2 ]; then
  serve $TAG ${PAIRS[0]} 8921 $T/${TAG}.jinja; serve ${TAG}pf ${PAIRS[1]} 8923 $T/${TAG}pf.jinja
else
  serve $TAG ${PAIRS[0]} 8921 $T/${TAG}.jinja;   serve $TAG ${PAIRS[1]} 8922 $T/${TAG}.jinja
  serve ${TAG}pf ${PAIRS[2]} 8923 $T/${TAG}pf.jinja; serve ${TAG}pf ${PAIRS[3]} 8924 $T/${TAG}pf.jinja
fi
probe() {  # name port: one drawing, greedy; logs how the reply splits into reasoning / content
  .venv/bin/python - $1 $2 <<'EOF'
import base64, json, sys, urllib.request, glob
sys.path.insert(0, "train_v14"); sys.path.insert(0, "train_v14/geom")
name, port = sys.argv[1], sys.argv[2]
png = open(sorted(glob.glob("mech_benchmarks/ext_bench_dw423_perm/**/*.png", recursive=True))[0], "rb").read()
body = {"model": name, "temperature": 0, "max_tokens": 2400, "chat_template_kwargs": {"enable_thinking": True},
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
            {"type": "text", "text": "Write build123d code for this part."}]}]}
r = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=600))
m = r["choices"][0]["message"]; rc = m.get("reasoning_content") or m.get("reasoning") or ""
print(f"probe {name}: finish={r['choices'][0]['finish_reason']} reasoning {len(rc)} chars {rc[:80]!r} | "
      f"content {len(m.get('content') or '')} chars {(m.get('content') or '')[:120]!r}")
EOF
}
run() {  # name port benches
  for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$2/health > /dev/null && break; sleep 15; done
  curl -s -m 5 http://127.0.0.1:$2/health > /dev/null || { say "$1 :$2 never ready: $(tail -3 $O/logs/vllm_$1_$2.log)"; return 1; }
  say "$1 up on :$2"; probe $1 $2 2>&1 | tail -1
  # TAG=$1: eval_nemo names outputs ${TAG:-$NAME}, and this script's own TAG would send both variants to one stem
  NAME=$1 TAG=$1 PORT=$2 MTOK=2400 WORKERS=12 OUT=$O/results BENCHES="$3" bash nemotron/eval_nemo.sh > $O/logs/eval_$1_$2.log 2>&1
  say "$1 :$2 eval: $(tail -1 $O/logs/eval_$1_$2.log)"
  kill -TERM -- -$(cat $O/vllm_$2.pgid) 2>/dev/null
}
if [ ${#PAIRS[@]} = 2 ]; then
  run $TAG 8921 "real benchb full" & run ${TAG}pf 8923 "real benchb full" & wait
else
  run $TAG 8921 "real benchb" & run $TAG 8922 full & run ${TAG}pf 8923 "real benchb" & run ${TAG}pf 8924 full & wait
fi
say "FT EVAL DONE $TAG"
