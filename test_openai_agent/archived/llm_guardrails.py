# USAGE: python llm_guardrails.py

import asyncio

from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    ModelSettings,
    RunContextWrapper,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    TResponseInputItem,
    input_guardrail,
)


class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str


# 创建自定义的 OpenAI 客户端
custom_client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-kcgyrk")
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    model="Qwen3-0.6B-FP8",
    model_settings=ModelSettings(
        temperature=0.6,
        top_p=0.95,
    ),
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    model="Qwen3-0.6B-FP8",
    model_settings=ModelSettings(
        temperature=0.6,
        top_p=0.95,
    ),
    input_guardrails=[math_guardrail],
)


async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")


if __name__ == "__main__":
    asyncio.run(main())
