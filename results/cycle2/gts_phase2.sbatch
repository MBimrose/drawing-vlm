#!/bin/bash
#SBATCH --job-name=c2-gts2
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=36:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/logs/%x-%j.out
# Cycle 2 GT search, phase 2 (after the CADBench scoring job): one gt_search2.py pool over all corpora in global
# priority order, attached to the rp3 server of the gts_l40s.sbatch job (127.0.0.1:8620). Stops that job's phase-1
# stream (A_c4 at 13 workers; its rows are kept and excluded). The realpool2 starts are added when serv-20 finishes
# scoring B_rp2 (background watcher below).
#   sbatch --cpus-per-task=70 --mem=200G --dependency=afterany:<score job> --export=ALL,P1PID=<pid>,WORKERS=68 gts_phase2.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; C=results/cycle2; O=$C/search
S20=wpk-serv-20.mechse.illinois.edu
S=/dev/shm/bimrose2/c2gts2_$SLURM_JOB_ID; mkdir -p $S; trap "rm -rf $S" EXIT
# reuse an already staged venv on this node when present (Lustre staging took 37 min)
SRC=$(ls -d /dev/shm/bimrose2/c2gts_*/venv 2>/dev/null | head -1); SRC=${SRC:-$DV/.venv/}
rsync -a --copy-links ${SRC%/}/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
curl -s -m 5 http://127.0.0.1:8620/health >/dev/null || { echo "no rp3 server on :8620"; exit 1; }
echo "$(date) staged (venv from $SRC)"
python3 $C/build_starts.py --tag c2pol --corpora c4,c2,c1
[ -n "${P1PID:-}" ] && { kill $P1PID 2>/dev/null && echo "stopped phase-1 stream $P1PID"; sleep 5; }
python3 $C/make_keys_all.py --exclude $O/gts_c4_p1.jsonl
( until ssh -o BatchMode=yes $S20 test -f /srv/scratch/bimrose2/cycle2/gen/SCORED_B_rp2_c2pol; do sleep 120; done
  rsync -a $S20:/srv/scratch/bimrose2/cycle2/gen/B_rp2_c2pol.json $C/gen/
  python3 $C/build_starts.py --tag c2pol --corpora rp2
  python3 $C/make_keys_all.py --exclude $O/gts_c4_p1.jsonl --exclude $O/gts_all.jsonl
  touch $O/RP2_STARTS_DONE; echo "$(date) rp2 starts added" ) &
BD=$DV/train_v14/mech/benchmarks/data
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
$PY $DV/train_v14/geom/gt_search2.py --bench c4=$BD/rft_corpus4,c2=$BD/rft_corpus2_dw423,c1=$BD/rft_corpus_dw423,rp2=$BD/rft_realpool_v2 \
  --starts c4=$O/starts_c4.json,c2=$O/starts_c2.json,c1=$O/starts_c1.json,rp2=$O/starts_rp2.json --keys $O/keys_all.txt \
  --until-file $O/RP2_STARTS_DONE --base-url http://127.0.0.1:8620/v1 --model rp3 --k 8 --rounds 4 --workers ${WORKERS:-68} \
  --py $PY --rpy $RPY --script-dir $S/step_to_drw --out $O/gts_all.jsonl > $C/logs/gts_all.log 2>&1
echo "C2 GTS PHASE2 DONE $(date)"
