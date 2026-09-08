#!/usr/bin/env bash
# Cluster tail of the draftwright-0.4.23 re-render (RECIPE "Training sheets re-rendered with draftwright 0.4.23"):
# once rerender_finish_serv19.sh reports done, copy tars_v14_dw423 + the strict90_dw423 shards back, build the
# legacy-holdout eval cache, build the RFT mix (78 base + 5x union5 + 8x GT links), submit e55, launch the
# shipper, and submit the new-renderer benches when the final exists.
#   setsid nohup train_v14/serv19/rerender_finish_cluster.sh > logs/rerender_finish_cluster.log 2>&1 < /dev/null &
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
S19=wpk-serv-19.mechse.illinois.edu; W=$DV/step_to_drw/wds_dataset; R=e55-rft-real-u5-gt-dw423
until ssh -o BatchMode=yes $S19 'grep -q "SERV19 FINISH DONE" /srv/scratch/bimrose2/logs/rerender_finish.log 2>/dev/null'; do
  if ssh -o BatchMode=yes $S19 'grep -q "FAILURE RATE\|without DONE" /srv/scratch/bimrose2/logs/rerender_finish.log 2>/dev/null'; then
    echo "$(date) serv-19 finisher aborted:"; ssh -o BatchMode=yes $S19 'tail -5 /srv/scratch/bimrose2/logs/rerender_finish.log'; exit 1; fi
  sleep 600; done
echo "$(date) serv-19 done; copying back"
rsync -a --exclude failures $S19:/srv/scratch/bimrose2/tars_v14_dw423/ $W/tars_v14_dw423/ || { echo rsync tars failed; exit 1; }
rsync -a $S19:/srv/scratch/bimrose2/tars_v14_dw423/failures/ $W/tars_v14_dw423_failures/
rsync -a $S19:/srv/scratch/bimrose2/logs/rerender_tars_dw423_summary.txt $S19:/srv/scratch/bimrose2/logs/rerender_tars_dw423.jsonl $W/tars_v14_dw423_failures/
rsync -a $S19:/srv/scratch/bimrose2/rft_strict90_all_dw423/shards/ $DV/rft_strict90_all_dw423/shards/ || { echo rsync shards failed; exit 1; }
echo "$(date) tars $(ls $W/tars_v14_dw423/shard_*.tar | wc -l), strict90_dw423 shards $(ls $DV/rft_strict90_all_dw423/shards | wc -l)"
# legacy residue-7 holdout cache on the new sheets (data_version 1 evals); v15 was built from the GT-STEP renders earlier
DRAWING_VLM_TARS=$W/tars_v14_dw423 DRAWING_VLM_EVAL_CACHE=$W/eval_cache_v14_dw423.pkl .venv/bin/python train_v14/build_eval_cache.py > logs/build_eval_cache_v14_dw423.log 2>&1; tail -2 logs/build_eval_cache_v14_dw423.log
# RFT mix in rft_mix_u6_gt's proportions: base + union5 x5 + ABC GT-code tier x8
bash train_v14/geom/build_rft_mix.sh $DV/rft_mix_u6_gt_dw423 $DV/rft_strict90_all_dw423/shards $DV/rft_real_union5_dw423/shards 5
i=$(ls $DV/rft_mix_u6_gt_dw423 | wc -l)
for r in 1 2 3 4 5 6 7 8; do for f in $DV/rft_real_abccode_train/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/rft_mix_u6_gt_dw423/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
echo "$(date) rft_mix_u6_gt_dw423: $i shards ($(ls -la $DV/rft_mix_u6_gt_dw423 | grep -c strict90) base, $(ls -la $DV/rft_mix_u6_gt_dw423 | grep -c union5) union5, $(ls -la $DV/rft_mix_u6_gt_dw423 | grep -c abccode) GT)"
[ -f $W/eval_cache_v15_dw423.pkl ] && [ "$(ls $DV/rft_mix_u6_gt_dw423 | wc -l)" -gt 40 ] || { echo "inputs incomplete, not submitting e55"; exit 1; }
J=$(sbatch --parsable train_v14/sbatch/$R.sbatch); echo "$(date) submitted $R: job $J"
setsid nohup train_v14/serv19/ship_finals.sh $R > logs/ship_finals_e55.log 2>&1 < /dev/null &
until [ -f runs/$R/final/model.safetensors.index.json ] && [ "$(ls runs/$R/final | wc -l)" -ge 10 ] && ! squeue -h -n $R -o %T | grep -q .; do sleep 600; done
B=$DV/train_v14/mech/benchmarks/data
J1=$(sbatch --parsable --export=ALL,RUN=$R,BENCH=$B/ext_bench_dw423,TAG=bo8_ext_dw423 --job-name=bo8-ext-dw423-e55 train_v14/sbatch/bo8_ext_cluster.sbatch)
J2=$(sbatch --parsable --export=ALL,RUN=$R,BENCH=$B/ext_bench_dw423_perm,TAG=bo8_ext_dw423p --job-name=bo8-ext-dw423p-e55 train_v14/sbatch/bo8_ext_cluster.sbatch)
echo "$(date) final exists; submitted new-renderer benches: ext_bench_dw423 job $J1, ext_bench_dw423_perm job $J2"
