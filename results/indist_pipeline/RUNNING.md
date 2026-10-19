# In-dist full pipeline (fullpool_dw423, 1,027 parts): what is running (started 2026-10-14 12:20 CDT)

Spec: bench-B S1/S2 protocol (results/bench_b/pipeline/summary_b.py docstring) on mech_benchmarks/fullpool_dw423.

## Layout
- S2 starts: `starts_e55vote_r{1,2,3}.json` = make_vote_picks.py on results/grpo_eval/full_e55ctl.json + _consistency.json
  (same command that reproduces bench-B starts_e55vote_r* byte-for-byte; checked). 0.917 / 0.875 / 0.857.
- S1 starts: `starts_rl2s60_r{1,2,3}.json` (pg_make_starts.py, after K=16 gen + stage 2) -- pending.
- Chains are split into blocks of 24 sorted keys: `blocks/<chain>.bNN.json` (make_blocks.py), chain names
  e55_c{1,2,3}, rl2s60_c{1,2,3}; 43 blocks each, list in `blocks.txt` (S1 first: runners skip blocks without picks).
- `runner.sh` (both hosts): claims a block by atomic mkdir in serv-20:/srv/scratch/bimrose2/indist_pipeline/claims/<block>
  (cluster runners via ssh), runs vr_serve.py (bench-B args) -> `out/<block>.jsonl`, then done/<block> + claims/<block>/DONE_<host>.
  Resumable: vr_serve skips finished keys; a host's claimed-but-unfinished blocks (mine/) are resumed by any runner of that host.
  Graceful drain: `touch STOP_<host>` in the host's ROOT (runners finish the current block, claim nothing new).
- Outputs live on the host that ran the block: cluster results/indist_pipeline/out/, serv-20 /srv/scratch/bimrose2/indist_pipeline/out/.
  Final: merge both out/ dirs -> chain_<chain>.jsonl (merge step in summary).

## Launched
| when | host | what | id |
|---|---|---|---|
| 10-14 12:23 | serv-20 GPUs 5,6 | S1 K=16 gen, rft2_rl_s60 merged (indist_pipeline/gen_k16.sh, vLLM DP2 :8710) | bash pid 1177731, vLLM pgid 1177736 |
| 10-14 12:26 | serv-20 GPU 4 | rp3 vLLM server :8721 (indist_pipeline/serve_rp3.sh 4 8721) | pid 1180373 |
| 10-14 12:31 | ccc0442 8 L40S, 84 CPU | chains_l40s.sbatch: rp3 TP2xDP4 :8730 + 7 runners x 12 workers | job 11445478 |
| 10-14 12:30 | serv-20 CPU | 5 runners x 12 workers -> rp3 :8721 (logs/runner_s20_r*.log) | pids 1202123 1202539 1207566 1213388 1219636 |
| 10-14 12:31 | ccc0442 40 CPU | stage2_full.sbatch: waits GEN_DONE, score/vote/render/v3 on ccc0442, verifier on serv-20 GPU 5, then S1 starts + blocks | job 11445498 |
| 10-14 12:44 | serv-20 CPU | runner 6 (12 workers -> :8721) | pid 2737773 |
| 10-14 12:46 | ccc0442 | job 11445478 vLLM up (16.6 min load); 7 runners started (logs/runner_c442_11445478_r*.log) | |
| 10-14 13:03 | ccc0442 (step in job 11445478) | tunnel_runners.sh tA: ssh tunnel :18722 -> serv-20 GPU 6 rp3 :8722 + 3 runners x 12 (srun launched from login node in background, pid 100573) | serv-20 GPU 6 server pid 874612 |
| 10-14 13:25 | ccc0442 | CANCELLED 11445478 (L40S server saturated ~14 rounds/min; scorers in Lustre D-state) and 11445498 (scoring 1.8 cand/s from Lustre) | |
| 10-14 13:26 | ccc0442 48 CPU | stage2_full_shm.sbatch (same steps, code+pool from /dev/shm/bimrose2/ipcode via stage_code_shm.sh; score resumes) | job 11446559 |
| 10-14 13:26 | ccc0442 78 CPU | chains_c442.sbatch: 7 runners x 12, rp3 via ssh tunnels to serv-20 :8721 (GPU 4) / :8722 (GPU 6), code from /dev/shm | job 11446560 |
| 10-14 13:45 | ccc0442 | CANCELLED 11446559/11446560: still D-state; cause = venv stdlib from uv Python homes on Lustre/NFS. Fix: stage_py_shm.sh (node-RAM Python homes) | |
| 10-14 13:46 | ccc0442 48 CPU | stage2_full_shm.sbatch (node-RAM code + Python) | job 11447226 |
| 10-14 13:46 | ccc0442 78 CPU | chains_c442.sbatch NR=7 W=12, tunnels to serv-20 :8721/:8722 | job 11447228 |
| 10-14 13:55 | serv-20 CPU | reaper.sh (kills this run's orphaned render_ext/exec/iou children, ppid 1) | pid 2544814 |
| 10-14 14:05 | serv-20 CPU | runners 7,8 (12 workers each -> :8722 GPU 6) | pids 4020973 4024270 |
| 10-14 14:20 | ccc0442 48 CPU | chains_c442.sbatch NR=4 W=12 (dependency afterany:11447226, takes stage-2 CPUs) | job 11450610 |
| 10-14 14:48 | serv-20 CPU | runners 9-11 (12 workers each -> :8721; block tails left serv-20 at ~44 busy) | pids 1144784 1147794 1151519  |
| 10-14 16:00 | note | coordinator: no lab-hub DeepSeek traffic. Checked: no script of this pipeline calls the hub; all vr_serve go to in-house rp3 vLLM (serv-20 :8721/:8722, directly or via ssh tunnel). The pre-existing bench_b ds_run.sh rollout is not part of this pipeline and was not touched. | |
| 10-14 16:40 | ccc0442 (step in 11447226) | cons_run.sh: consistency_rerank on 12 part-shards in parallel + merge (single-process K=16 pairwise would take ~7 h). Original single process left running; once merged file exists, kill it so stage2 proceeds | srun pid 1552779 |
| 10-14 17:35 | ccc0442 | stage-2 job 11447226 OOM-killed (job mem 300G; /tmp is RAM-backed rootfs, 13 consistency procs' STLs) at 17:26 with 5/12 shards done; render+v3 and vscore had finished. Remaining 7 shards: cons_run2.sh as srun step in job 11447228 (mem 500G). Queued job 11450610 (48 CPU, 4 runners) started 17:27 | srun pid 1913861 |
| 10-14 17:38 | serv-20 | killed runner 11 (pgid 1151519) to keep serv-20 busy count <= ~100; its claimed block e55_c2.b23 (0 parts done) is resumed by another serv-20 runner | |
| 10-14 19:30 | both | S1 part A: starts for the 771 parts of the 9 finished consistency shards (s1_partial.py + pg_make_starts.py -> partial/starts_rl2s60_a_r*.json), blocks rl2s60_c*.a.bNN queued first; remainder (shards 2,8,10) will be blocks rl2s60_c*.z.bNN from the full starts | |
| 10-14 20:36 | both | S1 part B: shards 8,10 (170 parts) -> partial/starts_rl2s60_b_r*.json, blocks rl2s60_c*.b.bNN. Only shard 2 (86 parts) still in consistency (RSS 150 GB) | |
| 10-14 21:36 | serv-20 CPU | runners 12,13 (-> :8722); qwenbase eval finished 17:32 | pids 758236 763098  |
| 10-14 23:03 | both | consistency merged (12 shards, 15713 re-executed) -> full_k16_rl2s60_consistency.json; full S1 starts starts_rl2s60_r{1,2,3}.json identical to part A/B on 941 keys; z blocks (86 keys/chain) queued. All work now queued. | |
| 10-15 03:55 | both | BUG FIX: part-B block names in blocks.txt lacked zero padding (b.b0 vs files b.b00), so the 24 part-B blocks (170 keys x 3 chains) were never claimed; fixed blocks.txt on both hosts | |
| 10-15 03:58 | both | the 24 unclaimed part-B blocks were reserved (claims/<b>/host = SPLIT, never run) and re-split into 48 blocks of 12 keys rl2s60_c*.c.bNN (shorter tail) | |
| 10-15 05:43 | both | ALL 285 blocks done (6 chains x 1,027 parts; validate.py: 0 missing / 0 dup / 0 empty rounds; no vr_serve errors or endpoint failures in any block log) | |
| 10-15 05:48 | both | TEARDOWN: STOP files; serv-20 runners 1-10,12,13 + reaper killed by pgid; rp3 servers GPU 4 (1180373) / GPU 6 (874612) killed; ccc0442 jobs 11447228, 11450610 cancelled | |
| 10-15 05:50 | cluster | out_s20/ = rsync of serv-20 out/; summary_full.py -> chain_{e55,rl2s60}_rp3_c{1,2,3}.jsonl + summary_full.txt | |

## STATUS: DONE (nothing running). Result: summary_full.txt.
