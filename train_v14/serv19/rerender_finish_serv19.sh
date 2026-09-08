#!/usr/bin/env bash
# serv-19 tail of the draftwright-0.4.23 re-render (RECIPE "Training sheets re-rendered with draftwright 0.4.23"):
# wait for rerender_tars.py to finish, summarise the failure log (abort if > 5% of attempted parts failed),
# pack the strict90 RFT base from the new tars, and flag completion for rerender_finish_cluster.sh.
#   setsid nohup ./rerender_finish_serv19.sh > logs/rerender_finish.log 2>&1 < /dev/null &
cd /srv/scratch/bimrose2
L=logs/rerender_tars_dw423.log
until grep -q "\[rerender\] DONE" $L || ! pgrep -u bimrose2 -f "[r]erender_tars.py tars" >/dev/null; do sleep 300; done
grep -q "\[rerender\] DONE" $L || { echo "$(date) tars driver exited without DONE"; exit 1; }
# no-fallback adapter (2026-09-08): re-attempt every recorded render failure once more through the
# fixed adapter (idempotent; appends recovered members to the finished shards)
while pgrep -u bimrose2 -f "[r]erun_failed_dw423.sh" >/dev/null; do sleep 120; done
# (exec_timeout included: the 120 s script timeout was load-induced while 256 workers ran)
.venv/bin/python mech_benchmarks/rerender_tars.py retry --tars $PWD/tars_v14 --out $PWD/tars_v14_dw423 --workers 64 \
  --retry-reasons render_legacy,render_fail,render_timeout,exec_timeout \
  --log logs/rerender_tars_dw423_retry.jsonl > logs/rerender_tars_dw423_retry_final.log 2>&1; tail -1 logs/rerender_tars_dw423_retry_final.log
python3 - <<'EOF' | tee logs/rerender_tars_dw423_summary.txt
import json, collections, glob
rs = [json.loads(l) for l in open("logs/rerender_tars_dw423.jsonl")]
err = [r for r in rs if "error" in r]; rs = [r for r in rs if "n_in" in r]
n_in = sum(r["n_in"] for r in rs); ok = sum(r["n_ok"] for r in rs); f = collections.Counter()
for r in rs: f.update(r["fails"])
skip = f.pop("skipped_known_bad", 0); att = n_in - skip; fail = att - ok
el = sum(r["elapsed"] for r in rs)
rec = 0
for p in glob.glob("tars_v14_dw423/failures/*.json"):
    rec += len(json.load(open(p)).get("recovered", []))
ok += rec; fail -= rec
print(f"shards {len(rs)} (+{len(err)} shard errors) parts {n_in} skipped_known_bad {skip} attempted {att} ok {ok} "
      f"(incl. {rec} recovered by the retry pass) failed {fail} ({100 * fail / max(att, 1):.2f}% of attempted) first-pass reasons {dict(f)}")
print(f"mean exec_s {sum(r['exec_s'] for r in rs) / len(rs):.1f} render_s {sum(r['render_s'] for r in rs) / len(rs):.1f} "
      f"shard elapsed {el / len(rs):.0f} s; worker-time {el / 3600:.0f} h")
c = collections.Counter()
for p in glob.glob("tars_v14_dw423/failures/*.json"):
    for k, v in json.load(open(p)).items():
        if k == "recovered" or v[0] == "skipped_known_bad": continue
        c[(v[0], v[1].split(":")[0][:60] if v[1] else "")] += 1
for k, v in c.most_common(15): print(v, k)
open("logs/rerender_tars_dw423_rate.txt", "w").write(f"{100 * fail / max(att, 1):.3f}\n")
EOF
rate=$(cat logs/rerender_tars_dw423_rate.txt)
if [ "$(echo "$rate > 5" | bc)" = 1 ]; then echo "$(date) FAILURE RATE $rate% > 5%: stopping before packing"; exit 2; fi
n=$(ls tars_v14_dw423/shard_*.tar | wc -l); echo "$(date) $n tars, failure rate $rate%"
DRAWING_VLM_TARS=$PWD/tars_v14_dw423 .venv/bin/python train_v14/geom/pack_rft_shards.py $PWD/rft_strict90_all_dw423 > logs/pack_strict90_dw423.log 2>&1
tail -1 logs/pack_strict90_dw423.log
echo "SERV19 FINISH DONE $(date)"
