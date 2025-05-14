# -*- coding: utf-8 -*-
# DESC: embedding server
# USAGE: python3 embedding_server.py

import uvicorn
import torch

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModel, AutoTokenizer
from contextlib import asynccontextmanager
from typing import List


# 超参数
MODEL_PATH = '../../model/BAAI/bge-m3'


embd_model = {}


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModel.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="cpu" # auto cpu
    )

    return tokenizer, model


@asynccontextmanager
async def lifespan(app: FastAPI):
    tokenizer, model = load_model()
    embd_model["tokenizer"] = tokenizer
    embd_model["model"] = model
    yield
    embd_model.clear()


app = FastAPI(lifespan=lifespan)


class Request(BaseModel):
    text: str
    normalize: bool = False


class Response(BaseModel):
    embedding: List[float]


def gen_embd(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model(**inputs)

    return outputs.last_hidden_state[:, 0, :]



@app.post("/generate")
async def generate(request: Request):
    embedding = gen_embd(text=request.text,
                         tokenizer=embd_model["tokenizer"],
                         model=embd_model["model"])

    if request.normalize:
            embedding = embedding / embedding.norm(dim=0, keepdim=True)

    return embedding.tolist()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9523, log_level="debug")
