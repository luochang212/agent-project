# mcp-project

MCP 实战

## 预研计划

MCP 只是 LLMs 生态中的一环，实现 MCP 需要多种前置服务的支持（比如 vLLM, LangChain）。 为了事先了解这些可能我也很陌生的服务，我必须像 Agent 一样，将任务拆分成多个子任务，再逐个进行预研。

本仓库的预研项目如下：

1. **Qwen3 推理脚本** ([/test_qwen3](/test_qwen3)):
   - 基于 vLLM 开发 qwen3 大模型推理服务
   - 基于 Ollama 开发 bge-m3 文本 embedding 推理服务
2. **简单的 RAG** ([/test_rag](/test_rag)):
   - 基于 LangChain 开发 RAG
   - 使用 qwen3, bge-m3 推理服务
   - 使用 chroma 作为向量数据库
<!-- 3. **简单的 MCP** ([/test_mcp](/test_mcp)):
   - 参考 anthropic 官方 MCP 教程，开发 MCP Server 和 MCP Client -->
3. **简单的 Qwen Agent** ([/test_qwen_agent](/test_qwen_agent)):
   - 对 sqlite 进行 CRUD 操作
   - 对 Redis 进行 CRUD 操作
   - 查询 postgresql 数据库
   - 使用 Qwen Agent 调用 FastAPI
   - 运行模型编排 Demo
4. **简单的 OpenAI Agent** ([/test_openai_agent](/test_openai_agent)):
   - 使用 `chat_completions` API 连接本地 vLLM 服务
   - 开发 Function Calling 示例
   - 开发 MCP 示例（SSE 方法）
   - 开发 Handoffs 示例
   - 开发 Central Agent 示例

> [!NOTE]
> 预研项目存放在以 `test_` 前缀命名的文件夹中。

## [正式项目]

to do ...
