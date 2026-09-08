# rft_real_abccode — real ABC parts with ground-truth build123d code (2026-09-08)

Supervision the model cannot self-generate: real ABC parts whose build123d program was recovered by
the user's mesh->CAD pipeline (MBimrose/agentic-mesh-to-cad, checkout serv-19:/srv/scratch/bimrose2/
CADFit_build123d, dataset/{ds0b,v1..v17}, banked at IoU >= 0.85 vs the source mesh), converted to our
dialect at 80 mm by train_v14/mech/benchmarks/convert_cadfit_program.py and verified at centred IoU
>= 0.99 against the banked STEP scaled by the same factor. Corpus: train_v14/mech/benchmarks/data/
rft_corpus_abccode (serv-19: mech_benchmarks/rft_corpus_abccode; old-renderer sibling
rft_corpus_abccode_dw400). Key = A_<8-digit ABC id>_code.

Counts: 523 candidate parts (523 unique ids in cadfit_abc_best.json, 0 held-out overlap) ->
432 converted+verified (319 plain .fuse/.cut, 9 kept the _safe_* helpers,
104 additionally polyline-cleaned: 162 Circle + 831 ThreePointArc replacements) -> rendered
432 (draftwright 0.4.0+font patch) / 429 (0.4.23+font patch) ->
429 scored by e51 best-of-8 under both renderings -> unsolved (best-of-8 < 0.8 on the 0.4.0 sheets)
192 (on the 0.4.23 sheets 225; both 178, only-0.4.0 14, only-0.4.23 47).
"Cannot write" is judged on the 0.4.0 renderer only (every training sheet so far is 0.4.0; the
0.4.23 renderer alone costs e51 0.07 on the held-out bench, see RECIPE.md).

Row format (rft_v1 accepted-*.jsonl, packed by train_v14/geom/pack_rft_shards_dir.py):
  {key, iou (= verified iou_vs_step of the GT program), ok: true, think: "", code (converted GT program),
   sample: 0, src: "gt", part_id, source_version, corpus_key, bo_best_dw400, bo_best_dw423, cadbench_filter_pass}

| dir | rows | sheets | keys |
|---|---|---|---|
| rft_real_abccode | 192 unsolved | draftwright 0.4.0+patch (render_dw400) | A_<id>_code |
| rft_real_abccode_dw423 | 192 unsolved (same parts) | draftwright 0.4.23+patch | A_<id>_code_dw423 |
| rft_real_abccode_all | 429 all scored parts | 0.4.0+patch | A_<id>_code |
| rft_real_abccode_all_dw423 | 429 all scored parts | 0.4.23+patch | A_<id>_code_dw423 |

Caveats: the source is a program-recovery pipeline, so the parts skew to what it can recover —
192 of the 429 scored parts (unsolved: 77 of 192) pass the CADBench single-body
filter of corpora 1-3 (aspect <= 15, fill >= 0.05, <= 120 faces, one solid); the rest are thin
profile extrusions (aspect > 15: 142), polyline-heavy programs (> 120 faces: 92) or multi-solid
compounds (50). cadbench_filter_pass in each row lets a mix filter them. Programs keep the emitter's
explicit Plane(origin, x_dir, z_dir) + BuildSketch/BuildLine style; think is empty (no plan text).
Per-part best-of-8 under both renderers: results/abccode_render_deltas_e51-rft-real-u3-strict90.json.
Data (png/, shards/, *.jsonl) is gitignored; README + stats.json + keys.txt are committed.
