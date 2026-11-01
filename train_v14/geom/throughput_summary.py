"""Throughput / latency table for the SFT + GRPO pipeline without repair on wpk-serv-05 (8x H200), from the
serve_full_timed.py records of throughput_s05.sh + plotpass_s05.sh (results/figures/pipeline_timing/throughput/).
Rows other than "bf16 (paper)" ran with up to 19 orphaned renders hogging cores (fixed 21 Oct 10:45), so CPU-bound rows
there understate throughput. Drawings/hour = parts / (last finish - first start); time per drawing = generate + execute + select, mean +- std.
-> throughput/summary.md, summary.json

    python3 train_v14/geom/throughput_summary.py
"""
import json
import os
import statistics as st

T = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/pipeline_timing/throughput"
ROWS = [  # file, serving, selection, test set, drawings in flight
    ("bf16_lat", "bf16", "verifier + render-compare", "Real (40 of bench B)", 1),
    ("fp8_lat", "FP8", "verifier + render-compare", "Real (40 of bench B)", 1),
    ("spec_lat", "FP8 + n-gram speculation", "verifier + render-compare", "Real (40 of bench B)", 1),
    ("v3_lat", "FP8", "render-compare", "Real (40 of bench B)", 1),
    ("single_c1", "bf16 (paper), 1 x H200", "render-compare", "Real (20 of bench B)", 1),
    ("single_c8", "bf16 (paper), 1 x H200", "render-compare", "Real (120 of bench B)", 8),
    ("single_c16", "bf16 (paper), 1 x H200", "render-compare", "Real (120 of bench B)", 16),
    ("single_c32", "bf16 (paper), 1 x H200", "render-compare", "Real (120 of bench B)", 32),
    ("bf16v3_v3_lat", "bf16 (paper)", "render-compare", "Real (40 of bench B)", 1),
    ("bf16v3_plotpass_bench_b", "bf16 (paper)", "render-compare", "Real (bench B)", 8),
    ("bf16v3_plotpass_fullpool_dw423", "bf16 (paper)", "render-compare", "Synthetic", 8),
    ("bf16v3_v3_acc", "bf16 (paper)", "render-compare", "Real (bench B)", 64),
    ("bf16v3_v3_tp", "bf16 (paper)", "render-compare", "Synthetic", 128),
    ("plotpass_bench_b", "FP8", "render-compare", "Real (bench B)", 8),
    ("plotpass_fullpool_dw423", "FP8", "render-compare", "Synthetic", 8),
    ("bf16_acc", "bf16", "verifier + render-compare", "Real (bench B)", 64),
    ("fp8_acc", "FP8", "verifier + render-compare", "Real (bench B)", 64),
    ("v3_acc", "FP8", "render-compare", "Real (bench B)", 64),
    ("bf16_tp", "bf16", "verifier + render-compare", "Synthetic", 128),
    ("fp8_tp", "FP8", "verifier + render-compare", "Synthetic", 128),
    ("v3_tp", "FP8", "render-compare", "Synthetic", 128),
]


def main():
    out, md = [], ["| Serving | Selection | Test set | In flight | Drawings | Drawings/hour | Time per drawing (s) | Mean IoU |",
                   "|---|---|---|---|---|---|---|---|"]
    for f, serv, sel, ts, c in ROWS:
        p = f"{T}/{f}.jsonl"
        if not os.path.exists(p):
            continue
        R = [json.loads(l) for l in open(p)]
        t = [r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"] for r in R]
        span = max(r["t_end"] for r in R) - min(r["t_start"] for r in R)
        iou = [r["iou_start"] for r in R if r.get("iou_start") is not None]
        o = {"run": f, "serving": serv, "selection": sel, "test_set": ts, "in_flight": c, "n": len(R), "per_hour": len(R) / span * 3600,
             "time_mean": st.mean(t), "time_std": st.stdev(t), "iou": st.mean(iou) if iou else None}
        out.append(o)
        md.append(f"| {serv} | {sel} | {ts} | {c} | {len(R)} | {o['per_hour']:.0f} | {o['time_mean']:.1f} ± {o['time_std']:.1f} | "
                  + (f"{o['iou']:.3f}" if iou else "–") + " |")
    open(f"{T}/summary.md", "w").write("\n".join(md) + "\n"); json.dump(out, open(f"{T}/summary.json", "w"), indent=1)
    print("\n".join(md))


if __name__ == "__main__":
    main()
