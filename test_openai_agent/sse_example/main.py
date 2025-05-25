import asyncio
import os
import shutil
import subprocess
import time

from typing import Any

from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


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
        instructions="Use the tools to answer the questions.",
        model="Qwen3-0.6B-FP8",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            temperature=0.6,
            top_p=0.9,
            tool_choice="required",
        ),
    )

    # Use the `add` tool to add two numbers
    message = "Add these numbers: 7 and 22."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # # Run the `get_weather` tool
    # message = "What's the weather in Tokyo?"
    # print(f"\n\nRunning: {message}")
    # result = await Runner.run(starting_agent=agent, input=message)
    # print(result.final_output)

    # Run the `get_secret_word` tool
    message = "What's the secret word?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8866/sse",
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # We'll run the SSE server in a subprocess. Usually this would be a remote server, but for this
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")

        print("Starting SSE server at http://localhost:8866/sse ...")

        # Run `uv run server.py` to start the SSE server
        process = subprocess.Popen(["uv", "run", server_file])
        # Give it 3 seconds to start
        time.sleep(3)

    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
