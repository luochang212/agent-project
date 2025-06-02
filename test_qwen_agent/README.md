# 简单的 Qwen Agent

Qwen Agent 为 Qwen 模型提供了很方便的工具调用和模型编排能力。

GitHub: [QwenLM/Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)

文件结构如下：

```
.
├── 1.llm.ipynb
├── 2.sqlite_bot.ipynb
├── 3.postgresql_bot.ipynb
├── 4.mysql_bot.ipynb
├── 5.redis_bot.ipynb
├── 6.fastapi_bot.ipynb
├── 7.orchestrating_multiple_agents.ipynb
├── README.md
├── assistant_mcp_sqlite_bot.py
├── fastapi_mcp_server.py
├── group_chat_chess.py
├── group_chat_demo.py
├── multi_agent_router.py
├── resource
│   └── poem.pdf
├── test.db
└── workspace
    └── tools
        ├── doc_parser
        │   └── 16693e49cf55d85733b3ecc032f3626ccbcde14a013d5711c6d5044e3fc2b372_without_chunking
        └── simple_doc_parser
            └── 16693e49cf55d85733b3ecc032f3626ccbcde14a013d5711c6d5044e3fc2b372_ori
```

其中，

- `1.llm.ipynb`: 使用 Qwen Agent 连接本地 vLLM 模型服务
- `2.sqlite_bot.ipynb`: 使用 Qwen Agent 对 sqlite 进行 CRUD 操作
- `3.postgresql_bot.ipynb`: 使用 Qwen Agent 查询 postgresql 数据库
- `4.mysql_bot.ipynb`: 使用 Qwen Agent 查询 MySQL 数据库
- `5.redis_bot.ipynb`: 使用 Qwen Agent 对 Redis 进行 CRUD 操作
- `6.fastapi_bot.ipynb`: 使用 Qwen Agent 调用 FastAPI
- `7.orchestrating_multiple_agents.ipynb`: 运行 Qwen Agent 模型编排 Demo
