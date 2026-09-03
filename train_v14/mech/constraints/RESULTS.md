# Mechanism 2 — constraints before code (2026-09-03)

Two-stage generation with a checkable intermediate: stage A reads the drawing
into a JSON constraint list (envelope, holes, pockets, chamfers, symmetry),
stage B writes the build123d script given drawing + constraints, then the
built mesh is measured (bbox extents, genus = through-passage count) and
compared with the constraint list; mismatches and tracebacks go back as
repair turns. Champion: `runs/e24-rft/final`. All code in this directory;
nothing outside it was edited.

Files
- `envelope_features.py` — CPU pass: executes stored candidates, records built
  extents / volume / genus, GT extents (diagnosis only), dims declared in the
  script, and the envelope stated in the `<think>` plan when one exists.
- `analyze_envelope.py` — the offline analyses below (no GT in any selector).
- `two_stage.py` — the GPU experiment (base arm + stage A + stage B + verify/repair).
- `m-constraints-envelope.sbatch`, `m-constraints-2stage.sbatch` — the jobs.
- `out/` — feature jsonl, analysis json, two-stage result json.

## Part 1 — offline, on the stored champion candidates (free)

Commands (job 10320749, CPU only, ~1.5 h on ccc0442):
```
sbatch train_v14/mech/constraints/m-constraints-envelope.sbatch
cd train_v14/mech/constraints && ../../../.venv/bin/python analyze_envelope.py \
    --bo8 out/env_bo8_full_e24.jsonl --scored out/env_scored_v1.jsonl \
    --out out/analysis_bo8_full_e24.json
```
Note: `results/bo8_full_e24.json` stores code + IoU only — no `<think>` text —
so "envelope stated in the think block" could only be tested on the RFT-scored
candidates (`rft_scored_v1/scored-*.jsonl`, training parts, which do carry the
plan), see 1c.

### 1a. How much of the failure mass is envelope-level? (7,278 executing candidates, 1,030 parts; GT used for diagnosis only)

| | |
|---|---|
| candidates whose built bbox matches GT bbox (±max(0.5 mm, 2%)) | 80.8% |
| IoU given envelope right / wrong | 0.930 (86% ≥0.85) / 0.688 (24% ≥0.85) |
| failing candidates (IoU<0.85, n=1,896) with a wrong envelope | **55.5%** |
| failing candidates with right envelope but wrong genus (hole count) | 17.7% |
| failing candidates with right envelope AND right genus | 18.0% |
| succeeding candidates with a wrong envelope | 6.3% |

So a bbox check would flag about half of the bad candidates at a 6% false-alarm
rate (AUROC 0.75 for "this candidate is wrong") — the signal is real at the
candidate level.

### 1b. But it does not change what gets served (selection on the stored 8×8 agreement matrices, 1,030 parts)

| selector (no GT) | mean IoU | ≥0.85 |
|---|---|---|
| first-to-execute | 0.878 | 72.8% |
| consistency medoid (deployed; reproduced) | **0.912** | **81.5%** |
| medoid restricted to the majority-envelope candidates | 0.908 | 80.8% |
| … and to the majority genus among those | 0.906 | 79.8% |
| oracle | 0.942 | 89.0% |

Per-part: the envelope gate changes 73 parts — 20 gains (+2.44 IoU total) vs
53 losses (−7.03). In 38 of the 53 losses the *majority* envelope is itself
wrong: the gate forces the model's misreading onto the vote. Why it cannot win:

- When the envelope is wrong it is wrong **by consensus**. The majority envelope
  is wrong on 151/1,025 parts (15%); only 68 parts have any envelope
  disagreement that the majority resolves correctly, and the medoid already
  sits inside the majority envelope on 952/1,025 parts (93%).
- The theoretical rescue set for an envelope check — medoid wrong (<0.85), its
  envelope wrong, majority envelope right — is **9 parts (0.9%)**; the maximum
  possible gain is < 0.005 mean IoU even if every one were fixed.
- Of the 108 unsolved parts (no candidate ≥0.85), 65 already have a candidate
  with the right envelope and 63 one with the right genus: the failures are
  internal feature placement/size, not the checkable quantities.
- Envelope disagreement across the 8 draws IS a confidence signal (medoid wrong
  in 7% of the 56% unanimous parts vs 32% of the rest; AUROC 0.77) but it is
  dominated by the medoid's own mean agreement (AUROC 0.87), which is already
  computed for the vote.

Conclusion of part 1: on stored candidates, a verifier that checks envelope +
hole count against a constraint list produced by the *same model* has ≤0.005
of headroom, because the model's constraint reading and its code share the
same misreadings. The mechanism can only pay off if stage A reads the drawing
better than the generator does — that is what the GPU experiment tests.

### 1c. Envelope stated in the model's own plan vs what it built (8,000 RFT-scored candidates with `<think>`, e16-class generator, training parts)

Proxy: the numbers in step 1 of the plan ("100 long by 60 wide by 8 thick").
It is a weak proxy — step 1 lists all three extents only ~40% of the time —
so read these as bounds: stated envelope covers GT 41%, built envelope right
66%, **stated-right-and-built-wrong 6.4%** (the most a "did the code do what
the plan said" check could recover), stated-wrong-and-built-right 32%. Plan/
build inconsistency has AUROC 0.59 for IoU<0.85. The plan is not a better
reading of the drawing than the code.

## Part 2 — GPU experiment: stage A → stage B → verify/repair (96-pool)

Command (job 10320760, ccc0442, 4×L40S, 1 h 50 min wall incl. 8 min model load):
```
sbatch train_v14/mech/constraints/m-constraints-2stage.sbatch
# = python train_v14/mech/constraints/two_stage.py --ckpt runs/e24-rft/final --kind hf \
#     --run e24-rft --n 96 --batch 8 --repair-rounds 2 --out train_v14/mech/constraints/out/two_stage_e24_96.json
```
Three arms in one model load on the same 96 parts (first 96 certified keys
with GT meshes = the standard 96-pool):
- **base**: greedy `build_gen_messages` + ≤2 exec-error repair rounds
  (`feedback_text`), i.e. the champion's single-shot "repair IoU" protocol.
- **stage A**: a constraint-extraction system prompt (`STAGE_A_SYSTEM` in
  `two_stage.py`; JSON with envelope_mm, base_shape, holes[diameter, count,
  through, depth, positions], pockets_slots, chamfers, fillets, symmetry),
  greedy, 1,600 tokens. The champion, never trained on JSON, emitted a
  parseable object for **94/96** parts (the 2 failures are unquoted values such
  as `"size": 30 diameter`; those fell back to the envelope stated in the base
  arm's plan).
- **cons**: stage B = same generation prompt with the JSON appended to the user
  turn ("the script must satisfy every item; verify each against the
  drawing"), greedy; then verify: execute, measure bbox extents and mesh genus
  (through-passage count; the mesh is watertight after vertex merge on 85% of
  candidates), compare with the list (sorted extents ±max(0.5 mm, 2%); genus <
  required through holes+slots), and send tracebacks / mismatch text back as
  a repair turn (`cons_feedback`), ≤2 rounds. Every round's mesh is IoU-scored.

### Was stage A a better reading than the generator? No.

| on the 96 parts (GT used for this diagnosis only) | stage A constraint list | base arm's built part |
|---|---|---|
| overall envelope right | 73 (76%) | 75 (78%) |
| through-hole count right (86 parts with known genus) | 52 (60%) | 58 (67%) |
| envelope right where the other is wrong | 13 | 15 |

The 15 "stage A wrong, base right" parts mostly have base IoU 0.95–1.00: stage
A reports the plate thickness as the overall height (8 vs 24, 5 vs 8.5, 12 vs
15 …) where a boss or rib sits on the plate. The same model reads the same
drawing the same way in both prompts; the JSON is not an independent check.

### Before/after on the same 96 parts, same hardware, same job

| arm / policy | mean IoU | ≥0.85 | median | executes |
|---|---|---|---|---|
| stored greedy draw 0 (`bo8_verifier2_e24`, H200 run) | 0.804 | 69.8% | — | 89.6% |
| **base r0** (this job, greedy) | 0.829 | 70.8% | 0.962 | 92.7% |
| **base + 2 exec-repair rounds** (= leaderboard protocol; leaderboard says 0.844) | **0.846** | **71.9%** | 0.963 | 95.8% |
| cons r0 (stage A → stage B, greedy) | 0.785 | 63.5% | 0.950 | 89.6% |
| cons + 2 verify/repair rounds, last executing | 0.784 | 63.5% | 0.949 | 89.6% |
| cons + 2 rounds, fewest-mismatch round | 0.785 | 63.5% | 0.950 | 89.6% |
| served consistency medoid on the same 96 (stored) | 0.923 | 84.4% | — | — |

Per-part delta (cons final − base final): mean **−0.063**; 13 parts better by
>0.05, 21 worse by >0.05, 62 within ±0.05. The five worst deltas (−0.96 to
−1.00) are parts the base arm solved at 0.95–1.00 where the constrained
script never executed.

Split by whether the constraint list was right (round 0): with a correct
envelope (73 parts) cons is −0.017 vs base (noise); with a wrong one (23
parts) −0.124. Stage B only reproduces the given envelope on 63/86 executed
parts (it half-ignores the list — which is why the damage is not larger).

### What the verify/repair loop actually did

- 41 parts flagged after round 0: 10 execution failures + 31 constraint
  mismatches (22 envelope, 13 hole count). 19 of the 31 mismatched parts were
  in fact ≥0.85 — the list, not the part, was wrong (verifier precision 39%);
  13 wrong parts passed the check.
- After 2 repair rounds: **1** mismatch cleared (a false alarm: 0.92 → 0.89),
  28/30 remaining mismatched parts came back with byte-identical extents (the
  model re-emits essentially the same script when told its envelope is
  80×70×9 but "should" be 80×40×6), and all 10 execution failures repeated the
  same traceback three times (`Failed creating a chamfer, try a smaller
  length`, fillet radius too large, `ChFi3d_Builder: only 2 faces`). The
  constraint list's chamfer/fillet entries pushed stage B into edge-treatment
  code the base arm did not write, and the repair turn does not make it back
  off. Repair mean over the 41 parts: 0.626 → 0.621.
- The base arm's own repair recovered 3/7 failures (+0.018), as in the recipe.

## Verdict

**No — this mechanism does not plausibly move the full-pool served number by
>0.01, and as implemented it moves single-shot down by 0.06.** Two independent
measurements agree:

1. Offline, on all 8,240 stored candidates, the checkable quantities
   (envelope, hole count) are wrong by *consensus* when they are wrong: the
   rescue set for an envelope/genus check is 9/1,025 parts (<0.005 IoU), and
   gating the vote on them costs 0.004 (0.912 → 0.908) because it enforces the
   model's own misreadings on 38 parts.
2. Live, the same model's JSON constraint list is no more accurate than the
   geometry it builds (76% vs 78% envelope, 60% vs 67% hole count), so the
   verifier flags mostly correct parts, and the model does not act on the
   feedback (1/31 mismatches resolved, identical scripts and tracebacks
   re-emitted). Prepending the list also degrades generation (−0.043 at round 0,
   −0.017 even when the list is right) and raises execution failures from
   chamfer/fillet operations the list invites.

Best-of-8 + consistency is not tested here, but nothing in the numbers
suggests it would flip: the vote already encodes envelope/genus agreement
(medoid inside the majority envelope on 93% of parts), and 8 constrained
draws would start from a −0.04 to −0.06 lower per-draw quality.

What would have to be true for a constraint check to pay: (a) a constraint
reader that is genuinely more accurate than the generator — a different model,
or dimensions read from the drawing's text/OCR layer rather than the VLM —
and (b) a repair turn the champion actually follows (it currently treats
"your envelope is X but the drawing says Y" like an unactionable comment; RFT
with mismatch-feedback turns in the data would be needed). Neither exists
today; (b) alone is a training project, and (a) is where the 11% unsolved
parts are NOT (65/108 already have a right-envelope candidate).

Noise note: the 96-pool single-shot bar is ±0.04; the −0.063 mean delta with
21 vs 13 parts moved by >0.05 is at the edge of that bar, but the direction is
corroborated by the round-0 exec-rate drop, the repair-loop null, and the
offline full-pool gate loss, so the negative verdict does not rest on the
mean alone.

## Blockers / caveats
- `results/bo8_full_e24.json` has no `<think>` text, so the "think-stated
  envelope" test could only use RFT-scored training candidates (part 1c).
- Hole verification uses mesh genus (through passages), which cannot check
  blind holes, hole diameters or positions; 15% of candidates are not
  watertight after merge and skip the check.
- Stage A JSON parse is strict; 2/96 lists were lost to unquoted values.
