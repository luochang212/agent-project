# agent-project

Agent 实战

## 一、技术栈

- **前端**: `Gradio`
- **后端**: `Qwen Agent`
- **数据库**: `PostgreSQL`/ `MySQL`
- **MCP**: `server-postgres`/ `mysql-mcp-server`

## 二、正式项目

1. [智能路由](./2.intelligent_routing.ipynb)
2. [查询优化](./3.nl2sql.ipynb)

## 三、配置文件

LLM 和 数据库 配置在 `.env` 文件中，按律不上传。它的格式如下：

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_orders
DB_USER=admin
DB_PASSWORD=admin-password
```

> **Note:** 请在项目根目录下创建 `.env` 文件

## 四、本地运行

前置步骤：

1. 启动本地 LLM 服务，或者配置服务商的 API_KEY
2. 安装 & 构造 Postgres 样例数据

启动 Gradio：

```bash
# 简单的聊天 APP，无 SQL 查询功能
python gradio_app.py

# [Agent] 简单查询，无定制工作流
python gradio_postgres_agent.py

# [Workflow] 定制工作流，可以降低错误率，但查询速度较慢
python gradio_postgres_workflow.py
```

启动后，打开浏览器访问 [http://localhost:7860/](http://localhost:7860/)

如果你用了我的样例数据，可以用以下问题测试：

- 数据库中有哪些表
- 订单表中随便取几条uid我看看
- uid为104的用户有哪些订单
- 查询一下订单1004的物流状态
- 查询uid为104的用户的所有订单的物流状态

## 五、预研计划

[MCP](https://github.com/modelcontextprotocol/servers) 只是 LLMs 生态中的一环，实现 MCP 需要多种前置服务的支持（比如 vLLM, LangChain）。为了事先了解这些可能我也很陌生的服务，我必须像 Agent 一样，将任务拆分成多个子任务，再逐个进行预研。

本仓库的预研项目如下：

1. **Qwen3 推理脚本** ([/test_qwen3](/test_qwen3)):
   - 基于 vLLM 开发 qwen3 大模型推理服务
   - 基于 Ollama 开发 bge-m3 文本 embedding 推理服务
2. **简单的 RAG** ([/test_rag](/test_rag)):
   - 基于 LangChain 开发 RAG
   - 开发 bge-m3 推理服务
   - 使用 chroma 作为向量数据库
<!-- 3. **简单的 MCP** ([/test_mcp](/test_mcp)):
   - 参考 anthropic 官方 MCP 教程，开发 MCP Server 和 MCP Client -->
3. **简单的 Qwen Agent** ([/test_qwen_agent](/test_qwen_agent)):
   - 对 SQLite 进行 CRUD 操作
   - 对 Redis 进行 CRUD 操作
   - 查询 PostgreSQL 数据库
   - 查询 MySQL 数据库
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

## 六、开发日志

- [x] [Postgres](./postgres_client.py) / [MySQL](./mysql_client.py) 数据库元数据查询工具
- [x] [Postgres](./postgres_tool.py) / [MySQL](./mysql_tool.py) Qwen Agent 函数调用 Function Calling
- [x] [Postgres](./postgres_agent.py) / [MySQL](./mysql_agent.py) 带查询功能的简单 Agent（非流式输出）
- [x] [Postgres](./postgres_workflow.py) / [MySQL](./mysql_workflow.py) 用于优化查询的工作流
- [x] [gradio_ui](./gradio_ui.py) 定义 WebUI 样式
- [x] [gradio_app](./gradio_app.py) 简单的 LLM Chat APP（流式输出）
- [x] [gradio_postgres_agent](./gradio_postgres_agent.py) Postgres APP（流式输出）
- [x] [gradio_postgres_workflow](./gradio_postgres_agent.py) Postgres Workflow APP（流式输出）
