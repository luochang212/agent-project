# -*- coding: utf-8 -*-
# USAGE: python fastapi_mcp_server.py

import uvicorn

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP


app = FastAPI()


@app.get("/users/{user_id}", operation_id="get_user_info")
async def read_user(user_id: int):
    return {
        "user_id": user_id,
        "nationality": "China",
        "birthday": "2.12"
    }


mcp = FastApiMCP(app)
mcp.mount()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8351)
