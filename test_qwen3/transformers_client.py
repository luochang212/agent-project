# -*- coding: utf-8 -*-
# USAGE: python3 transformers_client.py
# REFS:
#   - https://github.com/luochang212/llm-deploy/blob/main/server/ds_vllm_bash_client.py
# UPDATE: 
#   uv pip install -U openai
#   pip list | grep openai


from openai import OpenAI
from openai.types.chat import ChatCompletion


# 超参数
API_KEY = "token-kcgyrk"
BASE_URL = "http://localhost:9494/v1"
MODEL_NAME = "Qwen3-4B-FP8"


# 初始化客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def chat_completion(
    prompt: str,
    chat_id: str = "0",
    model: str = MODEL_NAME,
    temperature: float = 0.6,
    top_p: float = 0.95,
    repetition_penalty: float = 1.1,
    max_new_tokens: int = 32768,
    add_generation_prompt: bool = True,
    enable_thinking: bool = True
) -> ChatCompletion:

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        top_p=top_p,
        extra_body={
            "repetition_penalty": repetition_penalty,
            "add_generation_prompt": add_generation_prompt,
            "max_new_tokens": max_new_tokens,
            "enable_thinking": enable_thinking,
            "chat_id": chat_id,
        }
    )
    return response


if __name__ == "__main__":
    # ----------------------------------------
    # -------------  单轮对话  ---------------
    # ----------------------------------------
    # response = chat_completion(prompt="俄罗斯最大的搜索引擎叫什么")
    # content = response.choices[0].message.content
    # print(content)

    # ----------------------------------------
    # -------------  多轮对话  ---------------
    # ----------------------------------------
    response = chat_completion(prompt="顾真真只有一个哥哥，叫钟齐北，请问钟齐北的妹妹是谁", chat_id="chat-1")
    content = response.choices[0].message.content
    print("[round 1]")
    print(content)

    response = chat_completion(prompt="顾真真的哥哥叫什么名字", chat_id="chat-1")
    content = response.choices[0].message.content
    print("[round 2]")
    print(content)
