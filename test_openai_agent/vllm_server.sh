#!/bin/bash
# DESC: vllm openai server
# USAGE: bash vllm_server.sh
# HELP: vllm serve --help
# REFS:
#   - https://github.com/luochang212/llm-deploy/blob/main/server/qwen_vllm_bash_server.sh
#   - https://github.com/QwenLM/Qwen-Agent/tree/main?tab=readme-ov-file#preparation-model-service

source $(conda info --base)/etc/profile.d/conda.sh
conda activate qwen3_vllm

model_name="Qwen3-0.6B-FP8"
CUDA_VISIBLE_DEVICES=0 vllm serve "../model/Qwen/${model_name}" \
    --served-model-name ${model_name} \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.98 \
    --tensor-parallel-size 1 \
    --enable-reasoning \
    --reasoning-parser deepseek_r1 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --api-key token-kcgyrk
