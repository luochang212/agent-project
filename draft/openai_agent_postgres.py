# USAGE: 
#   - npx @modelcontextprotocol/server-postgres postgresql://admin:admin-password@localhost:5432/ecommerce_orders
#   - python openai_agent_postgres.py

import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

import asyncio

from openai import AsyncOpenAI
from agents import (set_default_openai_client, set_default_openai_api,
                    Agent, Runner, ModelSettings)
from agents.mcp import MCPServer, MCPServerSse


# Postgres Agent 的指令
POSTGRES_INSTRUCTIONS = """
你是一个数据库查询助手，专门帮助用户查询和分析 PostgreSQL 数据库中的数据。

能力：
1. 数据库结构查询
2. 执行 SQL 查询

规则：
1. 始终确保 SQL 查询的安全性，避免修改数据
2. 以清晰易懂的方式呈现查询结果
"""


async def run(mcp_server: MCPServer):
    # 创建自定义的 OpenAI 客户端
    custom_client = AsyncOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="token-kcgyrk")

    # 使用 Chat Completions API
    set_default_openai_client(custom_client)
    set_default_openai_api("chat_completions")

    postgres_agent = Agent(
        name="PostgreSQL Assistant",
        model="Qwen3-0.6B-FP8",
        instructions=POSTGRES_INSTRUCTIONS,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            temperature=0.6,
            top_p=0.95,
        ),
    )

    result = await Runner.run(postgres_agent, "数据库中有几张表")
    print(result.final_output.strip())


async def main():
    # 数据库配置
    db_conn = "postgresql://admin:admin-password@localhost:5432/ecommerce_orders"

    async with MCPServerSse(
        name="SSE Python Server",
        params={"url": "http://localhost:8866/sse"},
    ) as server:
        await run(server)


if __name__ == '__main__':
    asyncio.run(main())
