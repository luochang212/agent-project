#!/bin/bash
# DESC: vllm openai server
# USAGE: bash vllm_server.sh
# HELP: vllm serve --help
# REFS:
#   - https://github.com/luochang212/llm-deploy/blob/main/server/qwen_vllm_bash_server.sh

source $(conda info --base)/etc/profile.d/conda.sh
conda activate qwen3_vllm

qwen3_model_path="../model/Qwen/Qwen3-0.6B-FP8"
vllm serve $qwen3_model_path \
    --served-model-name Qwen3-0.6B-FP8 \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.98 \
    --tensor-parallel-size 1 \
    --api-key token-kcgyrk
