"""A sqlite database assistant implemented by assistant"""
# USAGE: python assistant_mcp_sqlite_bot.py


import asyncio

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI


def init_agent_service():
    llm_cfg = {
        'model': 'Qwen3-0.6B-FP8',
        'model_server': 'http://localhost:8000/v1',
        'api_key': 'token-kcgyrk',
        'generate_cfg': {
            'top_p': 0.95,
            'temperature': 0.6,
        }
    }
    system = ('你扮演一个数据库助手，你具有查询数据库的能力')
    tools = [{
        "mcpServers": {
            "sqlite" : {
                "command": "uvx",
                "args": [
                    "mcp-server-sqlite",
                    "--db-path",
                    "test.db"
                ]
            }
        }
    }]
    bot = Assistant(
        llm=llm_cfg,
        name='数据库助手',
        description='数据库查询',
        system_message=system,
        function_list=tools,
    )

    return bot


def app_gui():
    # Define the agent
    bot = init_agent_service()
    chatbot_config = {
        'prompt.suggestions': [
            '数据库里有几张表',
            '创建一个学生表包括学生的姓名、年龄',
            '增加一个学生名字叫韩梅梅，今年6岁',
        ]
    }
    WebUI(
        bot,
        chatbot_config=chatbot_config,
    ).run()


if __name__ == '__main__':
    app_gui()
