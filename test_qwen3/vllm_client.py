# -*- coding: utf-8 -*-
# USAGE: python vllm_client.py
# REFS:
#   - https://github.com/luochang212/llm-deploy/blob/main/server/ds_vllm_bash_client.py
# UPDATE: uv pip install -U openai

from openai import OpenAI


openai_api_key = "token-kcgyrk"
openai_api_base = "http://localhost:8000/v1"


client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chat_completion(prompt, chat_id="0", model="Qwen3-0.6B-FP8"):
    chat_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=32768,
        temperature=0.6,
        top_p=0.95,
        presence_penalty=1.5
    )

    return chat_response


if __name__ == "__main__":
    response = chat_completion(prompt="介绍一下监督微调 (SFT) 的工作原理，它是如何对大模型的参数进行训练的？")
    content = response.choices[0].message.content
    print(content)
