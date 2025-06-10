# -*- coding: utf-8 -*-

"""
Gradio APP

一个用 Gradio 开发的 Chat WebUI 应用

使用方法:
1. 下载 Qwen3 模型
2. 启动 vLLM 服务：
    cd test_qwen3
    bash vllm_server.sh
3. 启动 Gradio 应用：
    python gradio_app.py
4. 打开浏览器访问：
    http://localhost:7860/
5. 建议的 Query：
    - 查一下编号 103 的用户的订单信息
    - 查一下该用户订单的物流状态
"""

from gradio_ui import create_ui
from qwen_agent.agents import Assistant


# Qwen Agent 的 LLM 配置
LLM_CFG = {
    'model': 'Qwen3-0.6B-FP8',
    'model_server': 'http://localhost:8000/v1',
    'api_key': 'token-kcgyrk',
    'generate_cfg': {
        'top_p': 0.95,
        'temperature': 0.6,
    }
}


def create_simple_bot(llm_cfg):
    agent = Assistant(
        llm=llm_cfg,
        name='SimpleBot',
        description='一个智能聊天机器人',
        system_message="你是一个乐于助人的AI助手"
    )

    return agent.run_nonstream


def create_pg_bot(llm_cfg):
    from postgres_workflow import PGWorkflow

    # Postgres 数据库配置
    db_config = {
        "host": "localhost",
        "port": "5432",
        "database": "ecommerce_orders",
        "user": "admin",
        "password": "admin-password",
    }

    # 实例化 Workflow
    pgwf = PGWorkflow(llm_cfg, db_config)
    return pgwf.workflow


def bot_decorator(bot, max_history=6):
    """将 bot 绑定到目标函数"""
    def decorator(func):
        def wrapper(message, history):
            return func(message, history, bot, max_history)
        return wrapper
    return decorator


# @bot_decorator(bot=create_simple_bot(LLM_CFG), max_history=6)
@bot_decorator(bot=create_pg_bot(LLM_CFG))
def generate_response(message, history, bot, max_history):
    if not message.strip():
        return message, history

    messages = [{'role': 'user', 'content': message}]
    # 保留最后 max_history 条历史记录
    messages = history[-max_history:] + messages
    response = bot(messages)

    content = response.strip() if isinstance(response, str) else response[-1].get("content").strip()
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": content})
    return "", history


if __name__ == "__main__":
    demo = create_ui(llm_func=generate_response)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False
    )
