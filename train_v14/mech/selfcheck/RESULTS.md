# Mechanism 1: visual self-check (render-back-and-compare), 96-pool, e24 champion

Date: 2026-09-03. Directory: `train_v14/mech/selfcheck/`. Logs: `logs/mech/selfcheck/`.

## Idea

The served candidate (best-of-8 consistency medoid) is executed, the resulting
part is rendered back into a dimensioned drawing in the dataset's style, and the
champion is asked — in its own serving conversation — to compare that drawing to
the original and output a corrected script. Dimension errors that the
traceback repair loop cannot see (wrong depth, hole spacing, missing pocket)
become visible.

## What was built

| file | role |
|---|---|
| `render_drawing.py` | **Fallback renderer.** STEP -> third-angle top/front/right + isometric (OCCT HLR via build123d `project_to_viewport`; hidden lines dashed), navy overall-extent dimensions on every view, hole callouts `N× ⌀d` with centre-position dims in the top view, title block with measured overall size + volume. 1920×1280 like the training sheets. |
| `exec_keep.py` | `exec_harness.py` semantics but also keeps the STEP (needed for HLR). |
| `prestage.py` | CPU: for the 96 keys of `results/bo8_verifier2_e24.json`, take the champion's stored full-pool candidates (`results/bo8_full_e24.json`), pick the served medoid from the stored 8×8 matrices (`results/bo8_full_e24_consistency_v2.json`), re-execute all 8 (STLs for agreement scoring), render the served part. Idempotent, `out/prestage/<key>/`. |
| `selfcheck_gen.py` | GPU: prompt = serving conversation + assistant(served script) + user([rendered drawing] + compare-and-correct instruction); greedy, thinking on, same template as serving. Executes and scores the revision (IoU vs GT, IoU vs served part, mean agreement with the other 7 stored candidates — the same reference set the served candidate's agreement is computed over). |
| `analyze.py` | Offline acceptance policies + before/after table. |
| `m-selfcheck-prestage.sbatch`, `m-selfcheck-gen.sbatch` | SLURM (CPU pre-stage; 4×L40S on ccc0442). |

**Renderer caveat.** The dataset's `draftwright` renderer (upstream
`MBimrose/step_to_drw`: `draw_generator.py`, `dimensions.py`, ...) is not in this
checkout (only `wds_dataset/` and `train/` were synced) and the cluster has no
GitHub access, so the render-back uses my own matplotlib/OCCT-HLR fallback. It
matches the sheet layout, line conventions and dimension style, but not the
full auto-dimensioning (wall thicknesses, pocket depths, radii/chamfers are
visible only as line work, not as numbers). Position dims get cluttered when a
part has ≥3 hole-diameter groups. Examples: `out/prestage/<key>/served_render.png`.

## Exact commands

```bash
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; M=$DV/train_v14/mech/selfcheck
sbatch $M/m-selfcheck-prestage.sbatch                          # job 10320776 (CPU, ~9 min with 12 workers)
sbatch --dependency=afterok:10320776 $M/m-selfcheck-gen.sbatch  # job 10320835 (4×L40S ccc0442)
$DV/.venv/bin/python $M/analyze.py --out $M/out/selfcheck_96.json
# single part, by hand:
$DV/.venv/bin/python $M/render_drawing.py part.step out.png
```

Baseline reproduced from the stored matrices: served (medoid) mean IoU on these
96 parts = **0.9231**, 84.4% ≥0.85 (the full-pool candidates for the 96 keys;
the notebook's 0.919 is on the separately drawn `bo8_verifier2` candidates).
