# USAGE: python download_qwen.py

from modelscope import snapshot_download

model_dir = snapshot_download(
    # 'Qwen/Qwen3-0.6B-FP8',
    'Qwen/Qwen3-4B-FP8',
    cache_dir='./'
)

print(f"model_dir: {model_dir}")
