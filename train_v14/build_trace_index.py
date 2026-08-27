"""One-time: consolidate traces_v14 into a single JSON index.

traces_v14/ holds three artifact types per uuid:
    {uuid}_trace.txt   the Kimi K3 reasoning trace
    {uuid}_gate.json   reverse-reconstruction gate: {"pass": bool, vol_diff_pct, ...}
    {uuid}_recon.py    the gate's reconstruction script (not needed for SFT)

Output JSON: {uuid: {"t": trace_text, "p": true|false|null}}
(p=null when the uuid was never gated — the ~5% audit didn't sample it).

Usage: python build_trace_index.py
"""
import json
import os
import sys

TRACES = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/traces_v14"
OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/traces_v14.json"


def main():
    names = os.listdir(TRACES)
    trace_files = [n for n in names if n.endswith("_trace.txt")]
    gate_files = {n[: -len("_gate.json")] for n in names if n.endswith("_gate.json")}
    print(f"[trace-index] {len(trace_files)} traces, {len(gate_files)} gates", flush=True)

    index = {}
    n_pass = n_fail = n_ungated = bad = 0
    for i, n in enumerate(sorted(trace_files)):
        uuid = n[: -len("_trace.txt")]
        try:
            with open(os.path.join(TRACES, n), encoding="utf-8", errors="replace") as f:
                text = f.read().strip()
        except OSError:
            bad += 1
            continue
        if not text:
            bad += 1
            continue
        gate_pass = None
        if uuid in gate_files:
            try:
                with open(os.path.join(TRACES, uuid + "_gate.json")) as f:
                    gate_pass = bool(json.load(f).get("pass", False))
            except Exception:
                gate_pass = None
        index[uuid] = {"t": text, "p": gate_pass}
        if gate_pass is True:
            n_pass += 1
        elif gate_pass is False:
            n_fail += 1
        else:
            n_ungated += 1
        if (i + 1) % 10000 == 0:
            print(f"[trace-index] {i + 1}/{len(trace_files)}", flush=True)

    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(index, f)
    os.replace(tmp, OUT)
    sz = os.path.getsize(OUT) / 1e6
    print(f"[trace-index] wrote {len(index)} traces -> {OUT} ({sz:.1f} MB)\n"
          f"  gate pass={n_pass}  fail={n_fail}  ungated={n_ungated}  bad={bad}")


if __name__ == "__main__":
    sys.exit(main())
