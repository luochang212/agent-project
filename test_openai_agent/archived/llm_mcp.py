# USAGE: python llm_mcp.py

import asyncio
import os
import shutil

from openai import AsyncOpenAI
from agents import (set_default_openai_client, set_default_openai_api,
                    Agent, Runner, ModelSettings)
from agents.mcp import MCPServer, MCPServerStdio


async def filesystem_mcp():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")

    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        await run(server)


async def run(mcp_server: MCPServer):
    # 创建自定义的 OpenAI 客户端
    custom_client = AsyncOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="token-kcgyrk")
    set_default_openai_client(custom_client)

    # 使用 Chat Completions API
    set_default_openai_api("chat_completions")

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
        model="Qwen3-0.6B-FP8",
        model_settings=ModelSettings(
            temperature=0.6,
            top_p=0.9,
            tool_choice="required",
        ),
        mcp_servers=[mcp_server],
    )

    message = "列出当前目录下的文件"
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(filesystem_mcp())
