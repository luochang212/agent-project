# -*- coding: utf-8 -*-
# DESC: transformers openai server
# USAGE: python3 transformers_server.py
# REFS:
#   - https://github.com/luochang212/llm-deploy/blob/main/server/ds_transformers_server.py
#   - https://platform.openai.com/docs/api-reference/chat/create
#   - https://github.com/openai/openai-quickstart-python
#   - https://fastapi.tiangolo.com/advanced/events/

import os
import collections
import torch
import transformers
import time
import uuid
import uvicorn

from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager


# 超参数
API_KEY = "token-kcgyrk" # 配置 API 密钥
MODEL_NAME = "Qwen3-4B-FP8"
MODEL_PATH = "../model/Qwen/Qwen3-4B-FP8"
MAX_HISTORY_LENGTH = 3


# 指定使用哪一块显卡
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


# 聊天记录管理
class MemoryBank:
    def __init__(self, max_length=10):
        self.max_length = max_length
        self._storage = collections.defaultdict(list)
    
    def get(self, chat_id):
        return self._storage.get(chat_id, [])
    
    def add(self, chat_id, message):
        if chat_id not in self._storage:
            self._storage[chat_id] = []
        
        self._storage[chat_id].append(message)
        
        # Trim history if exceeds max length
        if len(self._storage[chat_id]) > self.max_length * 2: # *2 because each exchange has 2 messages
            self._storage[chat_id] = self._storage[chat_id][-self.max_length * 2:]
    
    def clear(self, chat_id=None):
        if chat_id:
            self._storage.pop(chat_id, None)
        else:
            self._storage.clear()


memory_bank = MemoryBank(max_length=MAX_HISTORY_LENGTH)


llm_model = {}


def load_model():
    tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)
    model = transformers.AutoModelForCausalLM.from_pretrained(MODEL_PATH,
                                                              device_map='auto',
                                                              torch_dtype=torch.bfloat16)
    return tokenizer, model


@asynccontextmanager
async def lifespan(app: FastAPI):
    tokenizer, model = load_model()
    llm_model["tokenizer"] = tokenizer
    llm_model["model"] = model
    yield
    llm_model.clear()


app = FastAPI(lifespan=lifespan)
security = HTTPBearer()


class ChatMessage(BaseModel):
    role: str # "user", "assistant", "system"
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    max_new_tokens: Optional[int] = 38912 # reference: https://huggingface.co/Qwen/Qwen3-4B-FP8#best-practices
    temperature: Optional[float] = 0.6
    top_p: Optional[float] = 0.95
    repetition_penalty: Optional[float] = 1.1
    add_generation_prompt: bool = True
    enable_thinking: bool = True
    chat_id: str


def verify_token(credentials: HTTPBearer = Depends(security)):
    """验证 API_KEY"""
    if credentials.credentials != API_KEY:
        raise HTTPException(401, "Invalid API Key")


def model_infr(messages,
               chat_id,
               tokenizer,
               model,
               max_new_tokens,
               temperature,
               top_p,
               repetition_penalty,
               add_generation_prompt,
               enable_thinking
              ):
    """模型生成文本"""

    # fetch history from memory_bank
    history = memory_bank.get(chat_id)

    chats = history + messages
    text = tokenizer.apply_chat_template(
        chats,
        tokenize=False,
        add_generation_prompt=add_generation_prompt,
        enable_thinking=enable_thinking
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    think_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    answer_content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    # update memory_bank
    memory_bank.add(chat_id, messages[-1].model_dump())
    memory_bank.add(chat_id, {"role": "assistant", "content": answer_content})

    return think_content, answer_content


@app.get("/v1/models", dependencies=[Depends(verify_token)])
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "user",
                "permissions": []
            }
        ]
    }


@app.post("/v1/chat/completions", dependencies=[Depends(verify_token)])
async def create_chat_completion(request: ChatCompletionRequest):

    # 模型推理
    think_content, answer_content = model_infr(
        messages=request.messages,
        chat_id=request.chat_id,
        tokenizer=llm_model["tokenizer"],
        model=llm_model["model"],
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        repetition_penalty=request.repetition_penalty,
        add_generation_prompt=request.add_generation_prompt,
        enable_thinking=request.enable_thinking
    )

    # 输出排版
    lst = [
        think_content,
        answer_content
    ]
    content = "\n".join(lst)

    return {
        "id": f"chatcmpl-{str(uuid.uuid4())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_NAME,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content.strip()
            },
            "finish_reason": "stop"
        }]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9494, log_level="debug")
