# American-VLM screen (2026-10-26) training environment, identical paths on serv-19 and serv-05 (serv-05's copies came
# from serv-19): the e55 data (tars_v14_dw423 plain tier, rft_mix_u6_gt_dw423 RFT tier, v14_bundle reasoning tier).
export TRAIN_VENV=${TRAIN_VENV:-/srv/scratch/bimrose2/.venv} DRAWING_VLM_ROOT=/srv/scratch/bimrose2
export DRAWING_VLM_TARS=/srv/scratch/bimrose2/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=/srv/scratch/bimrose2/data/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=${DRAWING_VLM_RFT_SHARDS:-/srv/scratch/bimrose2/rft_mix_u6_gt_dw423}   # the rp3 recipe overrides
export DRAWING_VLM_BUNDLE=/srv/scratch/bimrose2/data/v14_bundle
export DRAWING_VLM_TRACES_JSON=/srv/scratch/bimrose2/data/traces_v14.json
export DRAWING_VLM_BAD_KEYS=/srv/scratch/bimrose2/data/exec_bad_keys_v14.txt
export WANDB_MODE=offline HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export HF_HOME=/srv/scratch/bimrose2/.cache/huggingface
