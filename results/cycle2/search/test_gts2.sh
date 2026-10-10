DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; O=$DV/results/cycle2/search; BD=$DV/train_v14/mech/benchmarks/data
V=$(ls -d /dev/shm/bimrose2/c2gts_*/ | head -1)
export OMP_NUM_THREADS=1
timeout 1500 ${V}venv/bin/python $DV/train_v14/geom/gt_search2.py --bench c2=$BD/rft_corpus2_dw423,c1=$BD/rft_corpus_dw423 --starts c2=$O/starts_c2.json,c1=$O/starts_c1_missing.json \
 --keys $O/test_keys.txt --base-url http://127.0.0.1:8620/v1 --model rp3 --k 8 --rounds 2 --workers 2 --py ${V}venv/bin/python --rpy ${V}dw_venv/bin/python --script-dir ${V}step_to_drw --out $O/test_gts2.jsonl
cat $O/test_gts2.jsonl | cut -c1-300
