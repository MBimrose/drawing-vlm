#!/bin/bash
#SBATCH --job-name=mirror-srv
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --nodelist=ccc0442
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/%x-%j.out
# American-VLM on the H200 nodes (2026-10-28, user: "the campus cluster and the 3 H200 nodes are now free"). The serv-05 /
# serv-19 stacks run unchanged on ccc0451/74/75 inside apptainer with $M bound to /srv/scratch/bimrose2 (srv_exec.sh), so
# configs, venvs (absolute shebangs, local accelerate patch) and scripts keep their paths. This job pulls what each stage
# needs, in groups that finish independently; each group touches $M/MIRROR_<group> when its copy is complete.
#   sbatch train_v14/sbatch/mirror_srv.sbatch            (PULL="g4 rp nemo finals nemoft grpo" by default; rerun = resync)
set -uo pipefail
B=/projects/illinois/eng/ece/wpk/bimrose2; M=$B/srvmirror; MH=$B/srvmirror_uvpython; MS=$B/srvmirror_software
S5=wpk-serv-05.mechse.illinois.edu; S19=wpk-serv-19.mechse.illinois.edu; R=/srv/scratch/bimrose2
mkdir -p $M/models $M/containers $M/amvlm/runs $M/nemotron/runs $M/tmp $MH $MS
say() { echo "$(date '+%m-%d %H:%M:%S') $*"; }
pull() {   # pull <host> <remote path> <local path>: 3 tries
  local i; mkdir -p "${3%/*}"; for i in 1 2 3; do
    rsync -a --partial -e "ssh -o BatchMode=yes -o Compression=no" "$1:$2" "$3" && return 0
    say "rsync $1:$2 failed (try $i)"; sleep 30; done; return 1
}
group() {   # group <name> <cmd...>: run the pulls, mark success
  local g=$1; shift; say "[$g] start"
  if "$@"; then touch $M/MIRROR_$g; say "[$g] DONE"; else say "[$g] FAILED"; fi
}
g4() {     # Glimmer / Gemma training + data (serv-05 .venv_g4 has the Gemma tied-head accelerate patch)
  pull $S5 $R/.venv_g4/ $M/.venv_g4/ &&
  pull $S5 /home/bimrose2/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu/ $MH/cpython-3.12.12-linux-x86_64-gnu/ &&
  ln -sfn cpython-3.12.12-linux-x86_64-gnu $MH/cpython-3.12-linux-x86_64-gnu &&
  pull $S5 $R/amvlm/train_v14/ $M/amvlm/train_v14/ &&
  pull $S5 $R/data/ $M/data/ && pull $S5 $R/rft_mix_u6_gt_dw423/ $M/rft_mix_u6_gt_dw423/ &&
  pull $S5 $R/tars_v14_dw423/ $M/tars_v14_dw423/ &&
  pull $S5 $R/models/gemma-4-31B-it/ $M/models/gemma-4-31B-it/ && pull $S5 $R/models/Muse-Glimmer-30B/ $M/models/Muse-Glimmer-30B/
}
rp() {     # vLLM image + CUDA (flashinfer JIT) + the Glimmer repairer, for extra repairer servers
  pull $S19 $R/containers/vllm-nemotron-3f1bcfd8.sif $M/containers/ &&
  pull $S19 /software/cuda-13.0/ $MS/cuda-13.0/ &&
  pull $S5 $R/amvlm/runs/am-glimmer-rp3recipe/final/ $M/amvlm/runs/am-glimmer-rp3recipe/final/
}
nemo() {   # Nemotron Super VL base + its training venv (serv-19)
  pull $S19 $R/.venv_nemo/ $M/.venv_nemo/ &&
  pull $S19 $R/models/Nemotron-3.5-Super-VL-120B-A12B-BF16/ $M/models/Nemotron-3.5-Super-VL-120B-A12B-BF16/
}
finals() { # SFT finals (GRPO / repairer starts) + the repairer training mix; Gemma final_vllm (fixed config + links into final) is on serv-19
  pull $S5 $R/rft_mix_rp3/ $M/rft_mix_rp3/ &&
  pull $S19 $R/amvlm/runs/am-gemma4-31b-e55recipe/final_vllm/ $M/amvlm/runs/am-gemma4-31b-e55recipe/final_vllm/ &&
  pull $S5 $R/amvlm/runs/am-gemma4-31b-e55recipe/final/ $M/amvlm/runs/am-gemma4-31b-e55recipe/final/ &&
  pull $S5 $R/amvlm/runs/am-glimmer-30b-e55recipe/final/ $M/amvlm/runs/am-glimmer-30b-e55recipe/final/
}
grpo() {   # GRPO / EI rollout pools, hard-key lists, eval benches, prefill templates, the eval + scoring code (serv-19)
  local d; for d in fp/h6/rft_corpus4 fp/h6/train_bench mech_benchmarks/rft_corpus2_dw423 mech_benchmarks/rft_realpool_v2 \
      mech_benchmarks/ext_bench_dw423_perm mech_benchmarks/bench_b mech_benchmarks/fullpool_dw423 cycle2/mix \
      american_vlm/templates; do
    pull $S19 $R/$d/ $M/$d/ || return 1; done
  rsync -a -e "ssh -o BatchMode=yes" "$S19:$R/fp/h6/*.txt" $M/fp/h6/ && pull $S19 $R/nemotron/eval_nemo.sh $M/nemotron/
}
nemoft() { pull $S19 $R/nemotron/runs/nemo-fullft-r2/best_model/ $M/nemotron/runs/nemo-fullft-r2/best_model/; }
for g in ${PULL:-g4 rp nemo finals nemoft grpo}; do group $g $g & done
wait; say "all groups exited"
