# mcp-project

MCP 实战

## 预研计划

MCP 只是 LLMs 生态中的一环，实现 MCP 需要多种前置服务的支持（比如 vLLM, LangChain）。 为了事先了解这些可能我也很陌生的服务，我必须像 Agent 一样，将任务拆分成多个子任务，然后逐个进行预研。

本仓库的预研项目如下：

- **简单的 MCP** ([/test_mcp](/test_mcp)): 根据 anthropic 官方 MCP 教程，开发 MCP Server 和 MCP Client
- **Qwen3 推理脚本** ([/test_qwen3](/test_qwen3)): 
    - 基于 vLLM 开发 qwen3 推理服务
    - 基于 Ollama 开发 bge-m3 推理服务
- **简单的 Qwen Agent** ([/test_qwen_agent](/test_qwen_agent)): to do ...
- **简单的 RAG** ([/test_rag](/test_rag)): 基于 LangChain 开发 RAG

> [!NOTE]
> 预研项目存放在以 `test_` 前缀命名的文件夹中。

## [正式项目]

to do ...
