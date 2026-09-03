# Mechanism 3 — ambiguity-aware handling of underdetermined drawings

Directory: `train_v14/mech/ambiguity/`. Logs: `logs/mech/ambiguity/`. Nothing in
`train_v14/geom/`, `results/` or `runs/` was edited; the champion's generation
logic is duplicated in `gen_underdet.py` with only the system prompt changed.

## TL;DR

* The 242 "underdetermined" eval sheets are the ones whose renderer dropped at
  least one dimension. In **111/242 the dropped dimension is the overall
  length (`m_env_width`)**; the rest lose a feature location (`dim_loc_*_z`,
  57), a slot/pocket/pad size (74) or several at once.
* **The model already resolves the missing length correctly.** On the 114 parts
  whose dropped dimension is an envelope axis, the candidates' modal value of
  that extent equals the GT to 3 % in **98/114 (86 %)**; 73 % of parts have a
  single extent cluster across all 8 draws; the vote picks the modal value 98 %
  of the time. The candidates get the *dropped* axis wrong 15 % of the time vs
  12 % for the *dimensioned* axes — barely different.
* **The vote-vs-oracle gap on underdetermined sheets is not the missing
  dimension.** Of 46 env-axis parts with an oracle−vote gap > 0.02, only 5 are
  "same shape, different length" (0.79 of the 5.25 summed IoU gap = 15 %); in
  38 the vote and oracle candidates have the *same* length and differ elsewhere
  (rod height, shell/solid, pocket depth — ordinary reading errors on crowded
  sheets).
* **Half of the underdetermined deficit is sheet complexity, not ambiguity.**
  Underdetermined sheets carry 10.1 dimensions (7.9 placed + 2.2 dropped) vs
  6.5 on determinate ones — the renderer drops dimensions on crowded sheets. A
  dimension-count-matched determinate slice votes 0.899 (80 % ≥0.85) vs 0.923
  for all determinate and 0.875 for underdetermined: matching complexity closes
  0.024 of the 0.048 gap.
* Upper bound for any "fix the missing extent" mechanism on this pool: the 16
  parts (of 1,030) whose modal length is wrong, plus the 4 where the vote is
  wrong on that axis while the oracle is right. Even fixing all of them at the
  oracle's IoU is ≈ +0.004 on the full pool.

## 1. Offline characterization (stored e24 candidates; no GPU)

Inputs: `results/bo8_full_e24.json` (code + GT IoU per candidate),
`results/bo8_full_e24_consistency_v2.json` (8×8 agreement matrices, per-part
selections), the renderer sidecars `step_to_drw/wds_dataset/tars_v14/*.renderers.json`
(`dims_placed` / `dims_unplaced` / annotation labels per tar key; extracted for
the 1,030 pool uuids into `pool_sidecar.json`), GT meshes `gt_meshes_v15/`.
The eval PNG in `eval_cache_v15.pkl` is byte-identical to the tar's PNG, so
the sidecar describes exactly the sheet the model saw (checked on 3 parts).

Commands:
```
python train_v14/mech/ambiguity/exec_cands.py --bo8 results/bo8_full_e24.json \
    --keys train_v14/mech/ambiguity/keys_exec_all.txt \
    --stl-dir train_v14/mech/ambiguity/out/stl_e24 \
    --out train_v14/mech/ambiguity/out/cand_geom_e24.jsonl --workers 22      # sbatch m-ambiguity-exec.sbatch (CPU, 13 min)
python train_v14/mech/ambiguity/analyze.py          # -> out/analysis_e24.json
python train_v14/mech/ambiguity/complexity.py
```
(`keys_exec_all.txt` = 242 underdetermined uuids + 120 random determinate controls, seed 0.)

### What was dropped (sidecar `dims_unplaced`, 242 parts)

| dropped dimension kind | parts | first-exec | vote | (≥0.85) | oracle | (≥0.85) | oracle−vote |
|---|---|---|---|---|---|---|---|
| `m_env_width` only (overall length) | 70 | 0.808 | 0.849 | 66 % | 0.901 | 76 % | 0.052 |
| `m_env_width` + others | 41 | 0.789 | 0.834 | 61 % | 0.878 | 76 % | 0.043 |
| `dim_loc_side_z` / `dim_loc_front_z` only | 57 | 0.852 | 0.883 | 75 % | 0.920 | 88 % | 0.037 |
| slot / pocket / pad sizes only | 74 | 0.861 | 0.915 | 81 % | 0.938 | 88 % | 0.023 |
| all underdetermined | 242 | 0.831 | 0.875 | 72 % | 0.913 | 82 % | 0.038 |
| determinate control (120) | 120 | 0.903 | 0.924 | 85 % | 0.955 | 93 % | 0.031 |

Axis mapping verified on 80 parts with all three envelope dims placed:
`m_env_width`→x, `m_env_depth`→y, `dim_height`→z (80/80). The dropped
`m_env_width` is the part's largest extent in 100/111 cases (the long overall
dimension is what the layout fails to fit).

### Do the candidates disagree on the missing extent?  Mostly no.

114 parts have an envelope axis dropped (x in all but 3). Per executing
candidate, relative extent error vs GT > 3 %:

| | dropped axis | dimensioned axes |
|---|---|---|
| underdetermined, env-axis parts | **15.3 %** | 11.6 % |
| determinate control, any axis | — | 6.1 / 4.8 / 7.5 % (x/y/z) |

Candidate agreement on the dropped extent (3 % clusters): mean modal share
0.92, mean 1.42 clusters/part, 73 % of parts have one cluster. Modal value vs
GT: **right in 98/114**, wrong in 16. The vote picks a candidate in the modal
cluster in 98 % of parts. The vote's own dropped-extent is wrong in 15 parts,
the oracle's in 13; only **4 parts** have vote wrong / oracle right.

The 16 modal-wrong parts show the model's default: it rounds to a stock size
(GT 70→80, 74→80, 83→80, 84→95, 90→80/100, 65→60, 45→40, 95→91). GT lengths
on these sheets are multiples of 10 in 91/111 and multiples of 5 in 95/111,
which is why "guess the round number that fits the scale" is right 86 % of the
time. Where the hole pattern is symmetric (57/103 parts with hole offsets),
`first offset + last offset = length` holds exactly; the model gets those right.

### Where does the oracle−vote gap come from, then?

Among the 46 env-axis parts with oracle−vote > 0.02: 5 are extent-only
(same dimensioned extents, different dropped extent) — summed gap 0.79 IoU —
and 38 have identical dropped extents, i.e. the disagreement is in other
features (summed gap ≈ 4.2 IoU). Twelve largest-gap sheets inspected by eye
(`out/analysis_e24.json` + PNGs): `65ca2e88` (all 7 candidates have x=100 right;
rod height read as 90/120/180/210 — vote 0.44, oracle 0.97), `4a10ebb4`
(x=80 right in all; shell-vs-solid volume 22k vs 44k — vote 0.32),
`4e2a8bce` (x=80 in all; two candidates exact, vote picks a 0.66),
`6b79fb4c` (5/8 candidates identical and wrong, vol 92k vs 51k GT — the
majority is a systematic misread), `1a0c1678` (the one genuine length case:
6/8 say 80, GT 70, oracle 0.93 vs vote 0.45). The underdetermined deficit is
dominated by ordinary misreads on crowded sheets where the majority is wrong.

### Complexity confound

`complexity.py`: underdetermined sheets have 14.3 annotations / 10.1 dimensions
(7.9 placed) vs 11.8 / 6.5 for determinate. Vote by total dimension count:

| dims | determinate n / vote / oracle | underdetermined n / vote / oracle |
|---|---|---|
| 0–6 | 418 / 0.923 / 0.947 | 48 / 0.898 / 0.929 |
| 7–9 | 276 / 0.931 / 0.956 | 87 / 0.851 / 0.883 |
| 10–12 | 77 / 0.901 / 0.951 | 63 / 0.890 / 0.939 |
| 13–16 | 16 / 0.923 / 0.958 | 32 / 0.883 / 0.929 |

Dimension-count-matched determinate slice (237 parts): vote 0.899 (80 %),
oracle 0.937 — vs 0.875 / 0.913 underdetermined. About half of the 0.048 gap is
explained by "these are the crowded sheets"; the remaining ~0.024 is what
ambiguity (plus whatever else correlates with a failed layout) costs.

## 3. "Vote by determinate features only" — extent-invariant agreement selectors

The stored 8×8 matrices are full-shape IoUs, so a selector that ignores the
dropped extent needs the candidate meshes: `shape_vote.py` reloads the STL
cache and recomputes three agreement matrices per part (`sbatch
m-ambiguity-shapevote.sbatch`, CPU, ~35 min for 174 parts; meshes > 60k faces
are treated as non-voters because their Monte-Carlo fallback costs 4 min/pair).
Selectors (no GT used):

* `plain` — medoid on raw pairwise IoU (the deployed selector, recomputed).
* `shape_all` — every candidate anisotropically scaled to a 100 mm box before
  the pairwise IoU (pure shape agreement).
* `shape_axis` — only the axis on which the candidates disagree most (largest
  coefficient of variation of extents) is normalised — the practical form of
  "ignore the unplaced extent" (the dropped axis is not known at serving time).
* `hybrid` — `shape_axis` agreement + 0.05 bonus for candidates in the modal
  extent cluster.
* `scaled` — plain medoid, then its *mesh* is rescaled on the max-CV axis to
  the modal candidate extent (upper bound on "fix the extent after the vote";
  produces a distorted mesh, not code).

Same parts, same stored candidates (`out/shape_vote_e24.json`):

| selector | 114 env-axis underdetermined: mean / ≥0.85 | 60 determinate ctrl: mean / ≥0.85 |
|---|---|---|
| first-to-execute | 0.805 / 54 % | 0.893 / 75 % |
| **plain medoid (deployed)** | **0.847 / 65 %** | 0.926 / 85 % |
| shape_all | 0.843 / 64 % | 0.928 / 87 % |
| shape_axis | 0.845 / 64 % | 0.928 / 87 % |
| hybrid | 0.838 / 63 % | 0.928 / 87 % |
| scaled (post-hoc extent fix) | 0.838 / 62 % | 0.926 / 85 % |
| oracle | 0.895 / 76 % | 0.955 / 92 % |

Ignoring the extent in the vote changes nothing on the underdetermined parts
(−0.002 to −0.009) and is within noise on the controls (+0.002). This is the
expected consequence of §1: the candidates already agree on the dropped extent
(one cluster in 73 % of parts), so removing it from the agreement removes no
disagreement; and snapping the medoid to the modal extent is a net loss because
the modal extent is already what the medoid has. Verdict: no selector-side
gain is available from the underdetermination.

## 2. Upstream convention and the prompt-level intervention

### What the renderer's convention is

The renderer source (draftwright: `draw_generator.py` / `dimensions.py`) is
not in this checkout (only `step_to_drw/wds_dataset`, docs and the trace
daemon are; the GitHub remote needs credentials from the login node), so the
convention was read off the data instead. The sidecar records *which*
dimensions the layout failed to place, so the dropped value is not a design
convention — it is the true value of a dimension the sheet ran out of room for
(README: "capped dimension counts"; the dropped one is the long overall length
in 100/111 cases, on sheets with 55 % more dimensions than average). What the
data says about the true value of the dropped length:

* the sheet is to scale (title block "1:1"/"1:2"), so it is measurable in
  proportion to the placed `m_env_depth` / `dim_height`;
* hole patterns are centred: `first offset + last offset = length` in 57/103
  parts with x-location dims (e.g. offsets 8 & 92 → 100);
* it is a stock-size number: multiple of 10 in 91/111, of 5 in 95/111, integer
  in 106/111.

### Prompt

`gen_underdet.py --variant convention` appends this paragraph to the
champion's `detailed` system prompt (user turn unchanged, thinking on,
draw 0 greedy + 7 draws at T=0.7, top-p 0.95, 2400 new tokens — identical to
the served policy):

> Note on omitted dimensions: sheets from this drafting system are drawn to one
> common scale and occasionally omit a dimension, most often the overall
> length of the part. When a dimension is not called out, never invent an
> arbitrary value. Derive it: hole patterns, slots and pockets are centred on
> the outline, so an overall length equals the first hole's offset from one
> edge plus the last hole's offset from the same edge (e.g. offsets 8 and 92
> give a length of 100), and a feature dimensioned from one edge sits at the
> mirrored offset from the opposite edge. If no such relation exists, measure
> the undimensioned extent in proportion to a dimensioned extent in the same
> view and round to a plausible stock size (overall sizes are usually
> multiples of 5 mm).

Run: `sbatch train_v14/mech/ambiguity/m-ambiguity-gen.sbatch` (ccc0442,
4×L40S, job 10320770) on all 242 underdetermined parts. Per-draw checkpoints
are scored against the *stored* champion candidates restricted to the same
draws, both through the unchanged `consistency_rerank.py`:
```
K=<k> sbatch --export=ALL,K=<k> train_v14/mech/ambiguity/m-ambiguity-score.sbatch
# -> out/bo<k>_underdet_{convention,baseline}_consistency.json
```
Caveat: the baseline candidates were generated on serv-19 (B300); this run is
on L40S. The recipe notes ±0.025 hardware noise on single-shot numbers, so only
the best-of-N + consistency numbers and the per-part pattern are informative.
Note the run is ~50 min per draw for 242 parts on this shared node (weights
took 30 min to load) — much slower than the recipe's 20–40 min per 96×8.

### K = 1 (greedy draw only; 242 parts)

| | exec | mean IoU | ≥0.85 |
|---|---|---|---|
| stored champion greedy (serv-19) | 211/242 | 0.739 | 55.8 % |
| convention prompt greedy (L40S) | 216/242 | 0.756 | 57.0 % |

Per-part delta: mean +0.017, median 0.000, 45 parts improved by >0.05, 44
worsened by >0.05, 153 unchanged — a symmetric reshuffle, i.e. decode noise,
not a directional effect. Split by what was dropped: env-axis parts 0.735 →
0.761, other parts 0.742 → 0.752. On the 16 parts where the candidates' modal
length was wrong, the greedy draw went 6 up / 4 down / 6 unchanged
(e.g. `4be3913a` 0.78 → 0.95, `10827958` 0.26 → 0.63, but `1a0c1678` 0.56 →
0.41 and `998fc804` 0.70 → 0.00): the prompt does not make the model measure.

### Best-of-K + consistency, same 242 parts, same first K draws, same selector

The generation job ran at ~53 min/draw and hit its 5 h limit after draw 4, so
the comparison is on the K=4 and K=5 checkpoints. Convention candidates were
executed, IoU-scored and reranked with the unchanged `consistency_rerank.py`
(jobs 10321923 / 10322190; their trailing baseline reranks were cancelled as redundant once the matrix-derived baseline was validated); the baseline is the stored champion candidates
restricted to the same draws, selected from the stored 8×8 matrices
(`baseline_subk.py`; it reproduces the job's K=1 numbers exactly, 0.739/55.8 %).
`compare_k.py 4`:

| K=4, 242 parts | baseline (stored) | convention prompt | Δ | parts up >0.05 / down >0.05 |
|---|---|---|---|---|
| executed candidates | — | 842/968 (87 %) | | |
| first-to-execute | 0.820 (60 %) | 0.827 (60 %) | +0.007 | 40 / 43 |
| **consistency medoid** | **0.845 (66 %)** | **0.842 (65 %)** | **−0.002** | 35 / 42 |
| oracle@4 | 0.877 (76 %) | 0.889 (74 %) | +0.011 | 27 / 25 |

`compare_k.py 5` (adds the fifth, sampled draw):

| K=5, 242 parts | baseline (stored) | convention prompt | Δ | parts up / down >0.05 |
|---|---|---|---|---|
| executed candidates | — | 1057/1210 (87 %) | | |
| first-to-execute | 0.831 (60 %) | 0.827 (60 %) | −0.005 | 38 / 44 |
| **consistency medoid** | **0.862 (69 %)** | **0.855 (67 %)** | **−0.007** | 33 / 38 |
| oracle@5 | 0.899 (78 %) | 0.898 (76 %) | −0.001 | 23 / 24 |

K=5 slices (medoid): env-axis-dropped 0.843 → 0.834 (−0.009), other dropped
0.879 → 0.875 (−0.004), modal-length-wrong 0.647 → 0.639 (oracle 0.672 →
0.736: the prompt occasionally produces the right length as *one* of the
candidates, but never as the majority). Convention-run medoid agreement 0.858
— the same confidence as the baseline on this slice.

By slice (medoid): env-axis-dropped parts 0.825 → 0.818 (−0.007), other
dropped 0.862 → 0.864 (+0.002); the 16 modal-length-wrong parts 0.623 → 0.646
(+0.023, i.e. one or two parts) with oracle 0.650 → 0.727. The prompt is
inert on the served number: it reshuffles which parts win and lose
(35 up / 42 down, symmetric), nudges the oracle by +0.01 (more diverse
candidates), and does not touch the vote.

## Verdict

* **Does the model already pick a consistent default for the missing
  dimension?** Yes: one extent cluster across the 8 draws in 73 % of env-axis
  parts, modal share 0.92, and the modal value equals the GT in 86 %. The
  default is "the round stock size that fits the scale / the centred hole
  pattern", which is also the generator's truth 82–86 % of the time.
* **Is the vote choosing the majority default, and is it wrong vs GT?** The
  vote picks the modal extent in 98 % of parts; it is wrong on that axis in 15
  of 114 parts, and in only 4 of those does the oracle candidate have it right.
* **Oracle−vote gap on underdetermined parts = 0.038**, of which ≈15 % is
  "same part, different dropped length" and ≈85 % is other features. The
  deficit vs determinate sheets (0.048) is half explained by dimension count
  (crowded sheets), not by the dropped dimension.
* **Prompt-level convention statement**: no effect on the served number
  (medoid −0.002 at K=4 and −0.007 at K=5 on the same 242 parts; symmetric
  per-part reshuffle; oracle +0.011 / −0.001). **Extent-invariant voting**: −0.002 to −0.009. **Post-hoc
  extent snapping**: −0.009.
* **Plausible full-pool gain: < +0.005** even in the most optimistic reading
  (fixing every modal-wrong length at the oracle's IoU ≈ +0.004 on 1,030
  parts); the realistic gain of any ambiguity-specific mechanism is 0.000.
  The mechanism does not move the served number by >0.01. What the
  underdetermined slice actually needs is the same thing the determinate
  slice needs on crowded sheets — fewer feature misreads when the majority of
  8 draws agrees on the wrong reading (e.g. `6b79fb4c`: 5/8 identical wrong
  volumes) — which is a generation problem, consistent with the recipe's
  "11 % unsolved are a generation problem".

## What did not work / blockers

* The draftwright renderer source is not in this checkout and the GitHub
  remote is not reachable without credentials from the login node, so the
  "convention" was inferred from the sidecars + GT rather than read from
  `draw_generator.py`.
* ccc0442 was shared with another mechanism's 4-GPU job: weight load took 30
  min and each 242-part draw 53 min (5× the recipe's rate), so K=8 did not
  fit in the 5 h allocation; K=4/K=5 checkpoints were scored instead. A K=8
  rerun needs ~8 h on an idle node (`m-ambiguity-gen.sbatch`, resume works
  from `out/bo8_underdet_convention.json.partial.json`).
* Two CPU jobs were OOM-killed by pathological candidate meshes / runaway
  scripts (167 GB RSS); fixed with `limited_exec.py` (24 GB RLIMIT_AS per
  candidate subprocess, applied to `consistency_rerank.py` through
  `run_limited.py` without editing it) and a 60k-face voter cap in
  `shape_vote.py`.
* The login node was fork-starved several times during the session
  (`fork: retry: Resource temporarily unavailable`); all compute ran under
  SLURM.

## Files

| file | role |
|---|---|
| `pool_sidecar.json` | renderer sidecar entries for the 1,030 pool uuids (dims_placed / dims_unplaced / labels) |
| `keys_underdet.txt`, `keys_det_control.txt`, `keys_exec_all.txt`, `keys_shapevote.txt` | part lists |
| `exec_cands.py`, `m-ambiguity-exec.sbatch` | execute stored candidates → `out/stl_e24/`, `out/cand_geom_e24.jsonl` |
| `analyze.py` → `out/analysis_e24.json` | §1 extent / default / gap decomposition |
| `complexity.py` | §1 dimension-count confound |
| `shape_vote.py`, `m-ambiguity-shapevote.sbatch` → `out/shape_vote_e24.json` | §3 selectors |
| `gen_underdet.py`, `m-ambiguity-gen.sbatch` → `out/bo8_underdet_convention.json.partial.json` (5 draws) | §2 generation with the convention prompt |
| `score_partial.py`, `m-ambiguity-score.sbatch`, `limited_exec.py`, `run_limited.py` → `out/bo{1,4,5}_underdet_convention*.json` | scoring + reranking of checkpoints |
| `baseline_subk.py` → `out/bo{K}_underdet_baseline_from_matrices.json`; `compare_k.py` | baseline best-of-K from stored matrices; before/after tables |
