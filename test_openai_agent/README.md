# OpenAI Agent

OpenAI 作为一家知名闭源公司，居然开源了一款 Agent，那我必须要试一下了。

- GitHub: [openai/openai-agents-python](https://github.com/openai/openai-agents-python)
- Doc: [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)

文件结构如下：

```
.
├── 1.llm.ipynb
├── 2.basic_func.ipynb
├── README.md
├── archived
│   ├── llm_guardrails.py
│   ├── llm_mcp.py
│   └── sample_files
│       ├── readme.md
│       ├── test.txt
│       ├── test1.txt
│       └── test2.txt
├── llm_treaming.py
├── message_filter.py
├── sse_example
│   ├── README.md
│   ├── main.py
│   └── server.py
└── vllm_server.sh
```

其中，

- `1.llm.ipynb`: 使用 OpenAI Agent 连接本地 vLLM 模型服务
- `2.basic_func.ipynb: 开发 Function Calling, MCP, Handoffs, Central Agent 的示例

> [!NOTE]
> 使用 OpenAI Agent 的 Function tools 时，需要在 vllm serve 中启用两个选项 `--enable-auto-tool-choice` 和 `--tool-call-parser hermes`。注意，这里的 `hermes` 是针对 Qwen 模型的配置，如果你使用 DeepSeek, LLaMA 或其他模型，需要去文档中查看对应模型的配置 [tool_calling](https://docs.vllm.ai/en/stable/features/tool_calling.html)。
