# Mechanism 1: visual self-check (render-back-and-compare) — 96-pool, e24 champion

Date: 2026-09-03. Code: `train_v14/mech/selfcheck/`. Working tree (STLs, STEPs, PNGs): `/scratch/bimrose2/mech_selfcheck/`
(the `/projects/…/wpk` group quota was hard-full at 14.91/15 T during this run; only JSON/MD outputs are mirrored under
`train_v14/mech/selfcheck/out/`). Logs: `/scratch/bimrose2/mech_selfcheck/logs/` (+ `logs/mech/selfcheck/` for the early jobs).

## Verdict (short)

**Null result. The champion does not use the second drawing.** Given [original sheet, draftwright sheet rendered from its
own served part, its served script] and an explicit compare-and-correct instruction, the e24 model re-emits its standard
numbered build plan from the original sheet and returns the same script on 86/96 parts; the 10 "changes" are cosmetic
(revision-vs-served part IoU 0.98–1.00). Served mean IoU 0.9231 → 0.9230 (always-accept), ≥0.85 fraction 84.4 % → 84.4 %,
0 parts improved or worsened by >0.05, two-way oracle +0.0001. On 12 of the 15 failing parts the mismatch is printed on the
rendered sheet (envelope off by 3–21 mm or volume off by 25–160 %) and the model still did not act on it. Plausible
full-pool gain: **0.000 ± 0.002** — not >0.01, not worth a full-pool run (which would cost ~4 h on 4×L40S for generation alone).
Zero reasoning traces (0/96) reference the render, a mismatch, or a comparison.

## What was built

| file | role |
|---|---|
| `prestage.py` | CPU. For the 96 keys of `results/bo8_verifier2_e24.json`: take the champion's STORED full-pool candidates (`results/bo8_full_e24.json`), pick the served candidate = consistency medoid from the stored 8×8 matrices (`results/bo8_full_e24_consistency_v2.json`; reproduces `per_part.consistency` on 92/96, the 4 differ only by 4-dp rounding ties), re-execute all 8 (STLs for agreement scoring) and keep the served STEP. |
| `exec_keep.py` | `exec_harness.py` semantics, additionally keeps the STEP. |
| serv-19 render | **Real draftwright renderer** (`wpk-serv-06:/srv/scratch/bimrose2/drawing-agent/vendor/step_to_drw/`, copied by the benchmarks agent to `serv-19:/srv/scratch/bimrose2/mech_benchmarks/step_to_drw`), driven with the benchmarks agent's `render_ext.py` (`worker_v11._process_one_part`, VLM_MODE=1): 96/96 sheets in 32 s, CPU only, 95 `renderer: draftwright` + 1 `legacy` fallback (05f14712), 22/96 sheets underdetermined (`dims_unplaced` non-empty). Sidecar: `out/render_draftwright_renderers.json`. |
| `render_drawing.py` | My matplotlib/OCCT-HLR fallback renderer (third-angle views + iso, overall dims, hole callouts) — built before the real engine was located; kept as `served_render_fallback.png`, **not used for the reported run**. |
| `selfcheck_gen.py` | GPU. Prompt = the serving conversation continued: system(detailed) / user[original sheet + USER_PROMPT] / assistant[served script] / user[rendered sheet + CHECK_PROMPT]. Greedy, thinking on, same chat template as serving, batch 4, 2,400 new tokens. Executes the revision and scores: IoU vs GT, IoU vs the served part, mean agreement with the other 7 stored candidates (same reference set as the served candidate's agreement). Guard: a batch with ≥2 degenerate outputs (`!!!!`, no code, or a SyntaxError) is skipped and left for a resume. |
| `analyze.py` | Offline acceptance policies + table (below). |
| `m-selfcheck-prestage.sbatch`, `m-selfcheck-gen-ccc0442-scratch.sbatch` | The SLURM scripts that produced the result. (`m-selfcheck-gen.sbatch`, `m-selfcheck-gen-ccc0441.sbatch` are the earlier, aborted variants.) |

## Exact commands

```bash
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; M=$DV/train_v14/mech/selfcheck; W=/scratch/bimrose2/mech_selfcheck
sbatch $M/m-selfcheck-prestage.sbatch                       # job 10320776, CPU, 96×8 executions + fallback renders, 9 min
# real renders (serv-19, CPU only):
rsync -a <96 served.step as <uuid>.step> wpk-serv-19.mechse.illinois.edu:/srv/scratch/bimrose2/mech_selfcheck/steps/
ssh wpk-serv-19 'cd /srv/scratch/bimrose2/mech_selfcheck && SCRIPT_DIR=/srv/scratch/bimrose2/mech_benchmarks/step_to_drw \
   /software/python-3.11.1/bin/python3 /srv/scratch/bimrose2/mech_benchmarks/render_ext.py --src steps --out render_draftwright --workers 16'
# → copied to $W/out/prestage/<key>/served_render.png; meta.json paths rewritten to /scratch
sbatch $M/m-selfcheck-gen-ccc0442-scratch.sbatch            # job 10322877, ccc0442 4×L40S, COMPLETED, 1 h 10 min (load ~25 min + 96 × 22 s)
$DV/.venv/bin/python $M/analyze.py --out $W/out/selfcheck_96.json --md $W/out/analysis.md
```

Aborted attempts (for the record): job 10320935 on ccc0441 GPUs 0–3 and 10321109 on ccc0441 GPUs 4–7 both hit the node's bad
L40S (token-corrupted scripts such as `bracket_thickness = = 8.0`, then whole batches of `!!!!`); their partial outputs are in
`out/aborted_ccc0441/` and are not used. ccc0441 should be avoided for generation.

## Before/after on the same 96 parts (same stored candidates, same served medoid)

n = 96; revisions executed 96/96; script changed by the model 10/96; no-code 0; render failures 0.

| policy | mean IoU | median | ≥0.85 | ≥0.5 | Δmean vs served |
|---|---|---|---|---|---|
| **served (consistency medoid, deployed)** | **0.9231** | 0.9869 | **84.4 %** | 96.9 % | — |
| always accept revision (`rev_if_exec`; every revision executed, so "always" = "only-if-executes") | 0.9230 | 0.9859 | 84.4 % | 96.9 % | −0.0001 |
| accept only if the model changed the script | 0.9230 | 0.9859 | 84.4 % | 96.9 % | −0.0001 |
| accept only if agreement does not drop (`rev_agree ≥ served_agree − 0.05`, stored 8×8 matrices) | 0.9230 | 0.9859 | 84.4 % | 96.9 % | −0.0001 |
| accept only if agreement rises | 0.9232 | 0.9869 | 84.4 % | 96.9 % | +0.0001 |
| gated to low-agreement parts (served agree < 0.8, n=12) | 0.9232 | 0.9869 | 84.4 % | 96.9 % | +0.0001 |
| two-way oracle max(served, revision) | 0.9232 | 0.9869 | 84.4 % | 96.9 % | +0.0001 |

Per-part deltas (always-accept): improved >0.05: **0**; worsened >0.05: **0**; |Δ| ≤ 0.05: 96. Largest movers: 0120e88c
0.992→0.979, 0b9e23e2 0.974→0.968 (both slight regressions, agreement also dropped, so the agreement gate rejects them),
05f14712 0.772→0.786 (the only gain). Low-agreement slice (served agree < 0.8, n=12): 0.738 → 0.740. Failing slice (served
IoU < 0.85, n=15): 0.638 → 0.638, oracle2 0.639.

## Diagnosis of the 15 failing parts (served IoU < 0.85)

"Visible" = the served part's sorted bounding-box extents differ from GT by ≥3 mm or its volume differs by >25 % — i.e. at
least one printed dimension / view on the rendered sheet contradicts the original. (`out/envelope_check.json`)

| key | served | rev | changed | agree | extent Δ (mm) | vol ratio | underdet. | mismatch |
|---|---|---|---|---|---|---|---|---|
| 02c2c534 | 0.302 | 0.302 | no | 0.59 | 10.0 | 2.25 | no | visible |
| 09dc90de | 0.385 | 0.385 | no | 0.73 | 0.0 | 2.60 | no | visible |
| 0580ef4e | 0.421 | 0.421 | no | 0.94 | 0.0 | 0.42 | yes | visible |
| 0a3681ac | 0.504 | 0.504 | no | 0.86 | 8.0 | 1.00 | no | visible |
| 10a652e2 | 0.582 | 0.582 | no | 0.70 | 5.0 | 0.95 | no | visible |
| 10827958 | 0.628 | 0.628 | no | 0.68 | 3.0 | 0.97 | yes | borderline |
| 06e3334c | 0.668 | 0.668 | no | 0.60 | 20.6 | 1.48 | no | visible |
| 090d59fe | 0.669 | 0.669 | no | 0.83 | 0.5 | 0.74 | yes | visible (volume) — sheets near-identical to the eye |
| 08734382 | 0.688 | 0.688 | no | 0.81 | 0.0 | 0.69 | no | visible (volume only) |
| 087bbb7a | 0.747 | 0.747 | no | 0.84 | 0.0 | 0.75 | no | visible (volume only) |
| 05f14712 | 0.772 | 0.786 | yes | 0.76 | 5.0 | 0.93 | no | visible |
| 0d2a56a4 | 0.777 | 0.777 | no | 0.87 | 0.0 | 1.14 | yes | invisible |
| 0b611efc | 0.790 | 0.789 | yes | 0.83 | 4.0 | 0.95 | no | visible |
| 024cdfc2 | 0.795 | 0.795 | yes | 0.75 | 4.0 | 0.98 | yes | visible |
| 03dfa680 | 0.835 | 0.835 | no | 0.88 | 0.0 | 1.08 | no | invisible |

- **Visible mismatch, model did nothing: 9/15** (extent errors up to 21 mm, volume ×2.6 or ×0.42 — e.g. 06e3334c the rendered
  plate is 20 mm larger than the original's; 09dc90de the rendered part has 2.6× the volume). The model returned the served
  script unchanged (or, in 3 cases, a cosmetically edited one with part IoU ≥ 0.98 vs the served part).
- **Visible only as a volume/thickness difference (thin-walled shells): 3/15** (090d59fe, 08734382, 087bbb7a): extents match to
  0.5 mm; the original and rendered sheets differ only in a wall/floor thickness label or a hidden-line pattern. Correctable in
  principle but hard to see.
- **Invisible on a dimensioned sheet: 3/15** (0d2a56a4, 03dfa680, 10827958): same envelope, volume within 15 %; the IoU loss is
  in feature placement that the drawing does not determine (2 of 3 are underdetermined sheets).
- What the model did in every case: its thinking is a numbered build plan of the ORIGINAL sheet ("using the printed ⌀24
  callout…", "…set qualitatively since they are not printed"), identical in form to its training rationales; 0/96 traces mention
  the render, a mismatch, or a comparison. The fine-tune has collapsed the behaviour onto (drawing → plan → code); the second
  image and the instruction are ignored. This is a capability/format limitation of the RFT'd champion, not of the renderer.

## What failed / caveats

- The champion's `served` baseline here is the full-pool candidates restricted to the 96 keys (0.9231 / 84.4 %), not the
  notebook's separately drawn `bo8_verifier2` candidates (0.919 / 82 %); all comparisons are within this one candidate set.
- Rendered sheets use a new random dimension-placement variant (seeded from md5(uuid)), so the dimension SET differs from the
  original sheet's variant even when the part is right (e.g. 000bc5ac got the same set by luck). That is the deployable
  setting (no access to the original variant at serving time) but means an exact label diff is not available.
- One-round, greedy only. A sampled multi-round loop was not tried: with 0/96 traces engaging with the task, more samples of
  the same behaviour will not help (cf. the notebook's adaptive-K result).
- Cluster: ccc0441's L40S corrupt generation (two aborts); the `/projects` group quota is full (worked around via /scratch).

## Full-pool cost and recommendation

Full-pool would be 1,030 × (8 executions + 1 draftwright render + 1 two-image greedy generation ≈ 22 s on 4 L40S) ≈ 6.5 h
generation + ~30 min CPU. **Not recommended**: the 96-pool result is 0.000 ± 0.001 on every acceptance policy, the two-way
oracle is +0.0001, and the diagnosis shows the model never performs the comparison. If this mechanism is revisited, the
prerequisite is a model that can act on a second image: (a) an SFT/RFT tier of (original sheet, sheet of a wrong candidate,
wrong script → GT script) pairs — the ingredients exist (105k scored RFT candidates + this renderer at 3 s/sheet), or (b) a
non-visual check: extract the rendered sheet's dimension labels from the draftwright sidecar (`annotations`), OCR the
original's, and feed the model the explicit numeric diff as text (the repair loop already accepts text feedback and the model
does act on that).

Files: `out/selfcheck_96.json` (per-part record: served/rev IoU, agreement, changed flag, think tail), `out/analysis.md`,
`out/envelope_check.json`, `out/render_draftwright_renderers.json`; per-part renders + STLs under `/scratch/bimrose2/mech_selfcheck/out/prestage/<key>/`
(`served_render.png` = draftwright, `served_render_fallback.png` = my fallback).
