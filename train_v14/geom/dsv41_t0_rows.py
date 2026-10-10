"""T0-regime GRPO round -> advantage-weighted rows + stats (2026-10-07). Input: dsv41_t0_rollout.py episodes
(G per part). Reward = final program's centred IoU if it executed, else 0. A = (r - group mean) / batch std;
zero-variance groups skipped. Trained row = the FINAL call of an episode that ended with a code block (exec failures
included = negative signal), with that call's exact context (earlier turns -> ctx.json), reasoning and reply.
Episodes whose last call produced no code (truncated / no block) are not trained but count in the group mean.
    python dsv41_t0_rows.py --eps runs/r00/ep.jsonl --tier runs/r00/tier --stats runs/r00/stats.json"""
import argparse, io, json, os, pickle, statistics, tarfile


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--eps", required=True); ap.add_argument("--tier", required=True)
    ap.add_argument("--stats", required=True); ap.add_argument("--adv", choices=["mean", "batchstd"], default="batchstd")
    ap.add_argument("--max-row-tokens", type=int, default=33000, help="skip rows whose final call is longer (prompt + output)")
    ap.add_argument("--bank", default="", help="guided GRPO (dsgrpo3): rationalized bank (dsv41_t0_rationalize.py); a part's "
                    "bank program joins its group as an extra member when it beats every sampled draw by >= --guide-margin")
    ap.add_argument("--guide-margin", type=float, default=0.05)
    a = ap.parse_args()
    eps = [json.loads(l) for l in open(a.eps)]
    groups = {}
    for e in eps:
        e["reward"] = e["iou"] if e.get("exec") else 0.0
        groups.setdefault((e["bench"], e["key"]), []).append(e)
    n_guided = 0
    if a.bank:
        bank = json.load(open(a.bank))
        for (b, k), es in groups.items():
            g = bank.get(k)
            if g and g.get("status") == "ok" and g["iou"] >= max(x["reward"] for x in es) + a.guide_margin:
                es.append({"bench": b, "key": k, "draw": "g", "reward": g["iou"], "iou": g["iou"], "exec": True, "guide": True,
                           "n_calls": 1, "output_tokens": g.get("output_tokens") or 0, "code": g["code"],
                           "turns": [{"context": [], "think": g["think"], "text": g["reply"], "code": g["code"], "stop": "end_turn",
                                      "input_tokens": 1111, "output_tokens": g.get("output_tokens") or 0, "exec": True, "iou": g["iou"]}]})
                n_guided += 1
    live = {g: es for g, es in groups.items() if len(es) > 1 and max(x["reward"] for x in es) - min(x["reward"] for x in es) > 1e-6}
    std = max(statistics.pstdev([x["reward"] for es in live.values() for x in es]), 0.05) if (a.adv == "batchstd" and live) else 1.0
    rows, too_long = [], 0
    for g, es in live.items():
        m = sum(x["reward"] for x in es) / len(es)
        for x in es:
            x["adv"] = (x["reward"] - m) / std
            last = x["turns"][-1] if x["turns"] else {}
            if not last.get("code") or last.get("stop") == "max_tokens" or abs(x["adv"]) < 1e-9:
                continue
            if (last.get("input_tokens") or 0) + (last.get("output_tokens") or 0) > a.max_row_tokens:
                too_long += 1; continue
            rows.append((x, last))
    os.makedirs(a.tier, exist_ok=True)
    pngs = {}
    for b in sorted({x["bench"] for x, _ in rows}):
        c = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"]
        for x, _ in rows:
            if x["bench"] == b:
                pngs[x["key"]] = c[x["key"]]["png"]
        del c

    def add(t, name, data):
        ti = tarfile.TarInfo(name); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
    with tarfile.open(os.path.join(a.tier, "t0-00000.tar"), "w") as t:
        for x, last in rows:
            n = f"{x['key']}__d{x['draw']}"
            add(t, n + ".png", pngs[x["key"]]); add(t, n + ".code.py", last["code"].encode())
            add(t, n + ".think.txt", (last.get("think") or "").encode()); add(t, n + ".reply.txt", (last.get("text") or "").encode())
            add(t, n + ".ctx.json", json.dumps(last.get("context") or []).encode()); add(t, n + ".adv.txt", f"{x['adv']:.6f}".encode())
    mean = lambda v: sum(v) / len(v) if v else 0.0
    eps = [x for es in groups.values() for x in es if not x.get("guide")]
    toks = sorted(x.get("output_tokens", 0) for x in eps)
    st = {"parts": len(groups), "samples": len(eps), "mean_reward": mean([x["reward"] for x in eps]),
          "best_of_g": mean([max(x["reward"] for x in es if not x.get("guide")) for es in groups.values()]),
          "first_draw": mean([next((x["reward"] for x in es if x["draw"] == 0), 0.0) for es in groups.values()]),
          "exec_rate": mean([float(bool(x.get("exec"))) for x in eps]),
          "code_rate": mean([float(bool(x.get("code"))) for x in eps]),
          "trunc_rate": mean([float(any(t.get("stop") == "max_tokens" for t in x["turns"])) for x in eps]),
          "calls_per_episode": mean([x["n_calls"] for x in eps]),
          "first_call_success": mean([float(bool(x["turns"]) and bool(x["turns"][0].get("exec"))) for x in eps]),
          "mean_completion_tokens": mean(toks), "median_completion_tokens": toks[len(toks) // 2] if toks else 0,
          "frontier_frac": len(live) / max(1, len(groups)), "rows": len(rows), "rows_too_long": too_long, "adv_std": std,
          "pos_rows": sum(x["adv"] > 0 for x, _ in rows), "neg_rows": sum(x["adv"] < 0 for x, _ in rows),
          "guided_groups": n_guided, "guided_rows": sum(bool(x.get("guide")) for x, _ in rows)}
    json.dump(st, open(a.stats, "w"), indent=1)
    print("[rows] " + json.dumps(st), flush=True)


if __name__ == "__main__":
    main()
