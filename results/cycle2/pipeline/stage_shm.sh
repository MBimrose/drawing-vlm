#!/bin/bash
# one persistent staged copy (no cleanup trap) of the venvs / renderer / vLLM image in ccc0442 RAM for the cycle-2 jobs
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; T=/dev/shm/bimrose2/c2stage; mkdir -p $T
rsync -a --copy-links $DV/.venv/ $T/venv/ & rsync -a --copy-links $DV/dw_venv/ $T/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $T/step_to_drw/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $T/vllm.sif & wait
$T/venv/bin/python -c "import build123d, scipy, PIL" && $T/dw_venv/bin/python -c "import draftwright, OCP" && touch $T/READY && echo STAGED
