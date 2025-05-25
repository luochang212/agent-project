# 简单的 OpenAI Agent 示例

import asyncio
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import (set_default_openai_client, set_default_openai_api,
                    Agent, Runner, ModelSettings)


async def main():
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
            top_p=0.95
        )
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())