#!/bin/bash
# Run a serv-05 / serv-19 command unchanged on a campus-cluster node (2026-10-28): apptainer with the Lustre mirror
# (mirror_srv.sbatch) bound to /srv/scratch/bimrose2, the uv Python store to /home/bimrose2/.local/share/uv/python (the
# venvs' interpreter links) and CUDA 13.0 to /software/cuda-13.0 (vLLM flashinfer JIT). The image only supplies a
# userland: training uses the mirrored venvs, serving uses `vllm` from the vLLM image itself.
#   bash srv_exec.sh <command ...>          (SIF=... to pick the image; default the vLLM-nemotron image once mirrored)
set -uo pipefail
B=/projects/illinois/eng/ece/wpk/bimrose2; M=$B/srvmirror
SIF=${SIF:-$M/containers/vllm-nemotron-3f1bcfd8.sif}
[ -f $SIF ] || SIF=$B/drawing_vlm/containers/vllm-dsv41.from-serv20.sif
LT=${LOCAL_TMP:-/tmp/bimrose2_srv}; mkdir -p $LT/home $LT/tmp
export APPTAINERENV_USER=$USER APPTAINERENV_LOGNAME=$USER APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_TMPDIR=$LT/tmp
[ -n "${CUDA_VISIBLE_DEVICES:-}" ] && export APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES
exec apptainer exec --nv --cleanenv --no-home --home $LT/home \
  --bind $M:/srv/scratch/bimrose2 --bind $B/srvmirror_uvpython:/home/bimrose2/.local/share/uv/python \
  --bind $B/srvmirror_software:/software --bind /tmp:/tmp --bind $B:$B \
  $SIF bash -c "$*"
