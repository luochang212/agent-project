# mcp-project

MCP 研究性开发计划

## 预研项目

MCP 只是 LLMs 生态中的一环，要实现 MCP 需要多种服务支持。为了搭建这些可能我也很陌生的服务，我像 Agent 一样，将任务拆分成多个子任务，分别进行预研。

> [!NOTE]
> 预研项目存放在以 `test_` 前缀命名的文件夹中。

- **MCP** ([test_mcp](/test_mcp)): 根据 anthropic 官方 MCP 教程，开发 MCP Server 和 MCP Client
- **Qwen3** ([test_qwen3](/test_qwen3)): 
    - 基于 vllm 开发 qwen3 推理服务
    - 基于 Ollama 开发 bge-m3 推理服务
- **Qwen Agent** ([test_qwen_agent](/test_qwen_agent)):  
- **RAG** ([test_rag](/test_rag)): 基于 langchain 开发 RAG

## [正式项目]

to do ...
