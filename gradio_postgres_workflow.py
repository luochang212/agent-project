# -*- coding: utf-8 -*-

"""
Postgres Workflow

使用定制的 Workflow 查询 Postgres 数据库

使用方法:
1. 下载 Qwen3 模型
2. 启动 vLLM 服务：
    cd test_qwen3
    bash vllm_server.sh
3. 启动 Gradio 应用：
    python gradio_postgres_workflow.py
4. 打开浏览器访问：
    http://localhost:7860/
5. 可以尝试以下问题：
    - 告诉我用户编号 103 的用户的订单信息
    - 查一下该用户订单的物流状态
"""

from gradio_ui import create_ui
from postgres_workflow import PGWorkflow


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


def create_workflow(llm_cfg):
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


@bot_decorator(bot=create_workflow(LLM_CFG))
def generate_response(message, history, bot, max_history):
    if not message.strip():
        return message, history

    messages = [{'role': 'user', 'content': message}]
    messages = history[-max_history:] + messages  # 保留最后 max_history 条历史记录
    response = bot(messages)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response.strip()})
    return "", history


if __name__ == "__main__":
    model_name = LLM_CFG['model']
    demo = create_ui(llm_func=generate_response,
                     tab_name="Gradio APP - Postgres Workflow",
                     main_title="Postgres Workflow Demo",
                     sub_title=f"{model_name}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False  # 内部使用时，必须为 False
    )
