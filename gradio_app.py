# -*- coding: utf-8 -*-

"""
简单的 Agent

和本地 vLLM 服务提供的模型聊天，纯 LLM 无 MCP

使用方法:
1. 下载 Qwen3 模型
2. 启动 vLLM 服务：
    cd test_qwen3
    bash vllm_server.sh
3. 启动 Gradio 应用：
    python gradio_app.py
4. 打开浏览器访问：
    http://localhost:7860/
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

    return agent


my_bot = create_simple_bot(LLM_CFG)


def generate_response(message, history, max_history=6):
    if not message.strip():
        return message, history

    messages = [{'role': 'user', 'content': message}]

    # 保留最后 max_history 条历史记录
    messages = history[-max_history:] + messages

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": ""})

    # 流式响应
    for chunk in my_bot.run(messages):
        content = chunk[-1].get("content", "")
        history[-1]["content"] = content
        yield "", history

    yield "", history


if __name__ == "__main__":
    model_name = LLM_CFG['model']
    demo = create_ui(llm_func=generate_response,
                     tab_name="Gradio APP - LLM",
                     main_title="Simple Agent Demo",
                     sub_title=f"{model_name}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False  # 内部使用时，必须为 False
    )
