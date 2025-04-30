# 开发 Qwen3 模型推理服务

文件结构如下：

```
.
├── 1.transformers.ipynb
├── 2.vllm.ipynb
├── README.md
├── transformers_client.py
├── transformers_server.py
├── vllm_client.py
└── vllm_server.sh
```

其中，

- `1.transformers.ipynb`: 简单使用 transformers 做 Qwen3 模型推理
- `2.vllm.ipynb`: 简单使用 vllm 做 Qwen3 模型推理
- `transformers_client.py`: transformers 客户端
- `transformers_server.py`: transformers 服务端启动脚本
- `vllm_client.py`: vllm 客户端
- `vllm_server.sh`:  vllm 服务端启动脚本

> [!NOTE]
> 对于 `transformers_server.py` 脚本，在生产环境中不要用 `class MemoryBank` 这种方式存储对话历史，要用 Redis 或者 PostgreSQL，虽然生产环境也不会用 transformers 就是了。
