from __future__ import annotations

import json
import random

from openai import AsyncOpenAI
from agents import (Agent, HandoffInputData, Runner, function_tool, handoff, trace,
                    set_default_openai_client, set_default_openai_api, ModelSettings)
from agents.extensions import handoff_filters


@function_tool
def random_number_tool(max: int) -> int:
    """Return a random integer between 0 and the given maximum."""
    return random.randint(0, max)


def chinese_handoff_message_filter(handoff_message_data: HandoffInputData) -> HandoffInputData:
    # First, we'll remove any tool-related messages from the message history
    handoff_message_data = handoff_filters.remove_all_tools(handoff_message_data)

    # Second, we'll also remove the first two items from the history, just for demonstration
    history = (
        tuple(handoff_message_data.input_history[2:])
        if isinstance(handoff_message_data.input_history, tuple)
        else handoff_message_data.input_history
    )

    return HandoffInputData(
        input_history=history,
        pre_handoff_items=tuple(handoff_message_data.pre_handoff_items),
        new_items=tuple(handoff_message_data.new_items),
    )


# 创建自定义的 OpenAI 客户端
custom_client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-kcgyrk")
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")


first_agent = Agent(
    name="Assistant",
    model="Qwen3-0.6B-FP8",
    instructions="Be extremely concise.",
    tools=[random_number_tool],
)

chinese_agent = Agent(
    name="Chinese Assistant",
    model="Qwen3-0.6B-FP8",
    instructions="You only speak Chinese and are extremely concise.",
    handoff_description="A Chinese-speaking assistant.",
)

second_agent = Agent(
    name="Assistant",
    model="Qwen3-0.6B-FP8",
    instructions=(
        "Be a helpful assistant. If the user speaks Chinese, handoff to the Chinese assistant."
    ),
    handoffs=[handoff(chinese_agent, input_filter=chinese_handoff_message_filter)],
)


async def main():
    # Trace the entire run as a single workflow
    with trace(workflow_name="Message filtering"):
        # 1. Send a regular message to the first agent
        result = await Runner.run(first_agent, input="Hi, my name is Sora.")

        print("Step 1 done")

        # 2. Ask it to generate a number
        result = await Runner.run(
            first_agent,
            input=result.to_input_list()
            + [{"content": "Can you generate a random number between 0 and 100?", "role": "user"}],
        )

        print("Step 2 done")

        # 3. Call the second agent
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "I live in New York City. Whats the population of the city?",
                    "role": "user",
                }
            ],
        )

        print("Step 3 done")

        # 4. Cause a handoff to occur
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "我的名字是什么，我住在哪里？",
                    "role": "user",
                }
            ],
        )

        print("Step 4 done")

    print("\n===Final messages===\n")

    # 5. That should have caused chinese_handoff_message_filter to be called, which means the
    # output should be missing the first two messages, and have no tool calls.
    # Let's print the messages to see what happened
    for message in result.to_input_list():
        print(message)
        # print(json.dumps(message, indent=2))
        # tool_calls = message.tool_calls if isinstance(message, AssistantMessage) else None

        # print(f"{message.role}: {message.content}\n  - Tool calls: {tool_calls or 'None'}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())