# USAGE: python download_qwen.py
# URL: https://www.modelscope.cn/models/BAAI/bge-m3

from modelscope import snapshot_download

model_dir = snapshot_download(
    'BAAI/bge-m3',
    cache_dir='./'
)

print(f"model_dir: {model_dir}")
