# -*- coding: utf-8 -*-

"""
定制的 Postgres 数据库查询流程，增加查询成功率

主要步骤：
1. 确认需要用到的数据表
2. 查询可能用到的表和表结构
3. 将表名和表结构作为上下文，注入原始查询

适用性：
  只接受需要用到一张表的情况，如果需要多张表和表结构，需要额外开发
"""

from datetime import datetime
from postgres_agent import PGAgent


class PGWorkflow(PGAgent):
    """Postgres Workflow"""

    def __init__(self, llm_cfg, db_config=None):
        super().__init__(llm_cfg, db_config)
        self.llm_cfg = llm_cfg

        # Postgres 数据库配置
        # 允许 db_config 为 None，为 None 时使用 .env 中的配置
        self.db_config = db_config
        self.set_db_config()

        # 创建 Agents
        self.agents = dict()
        self.register()

    def register(self):
        """注册 Agents"""
        self.agents = {
            'react': self.create_react_agent(),
            'assistant': self.create_assistant_agent(),
        }

    def workflow(self, messages: list) -> list:
        """定制的查询 workflow，可提高查询成功率，但速度较慢"""

        react_bot = self.agents['react']
        assistant_bot = self.agents['assistant']

        # 提取用户 query
        query = messages[-1].get('content', '').strip()

        # 1. 定位数据表
        first_response = assistant_bot.run_nonstream(messages[:-1] + [
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "你不需要回答用户提问。你需要：",
                    "1. 请先调用工具查询 Postgres 数据库中有哪些表",
                    "2. 然后思考用户提问中，可能用到其中哪些表",
                    "注意，最终返回结果中，只需包含你认为可能用到的表，不要有多余的文字。如果没有可用表，回答无可用表。",
                ])
            }
        ])

        
        first_message = first_response[-1].get('content').strip()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 如果没有可用表，直接返回
        if "无可用表" in first_message:
            return messages[:-1] + [
                {
                    'role': 'user',
                    'content': "\n".join([
                        f"当前时间：{now}",
                        "",
                        "用户问题如下：",
                        f"{query}",
                        "",
                        "请你调用 Postgres 数据库查询工具，回答用户的问题。",
                    ])
                }
            ]

        # 2. 查询表结构
        second_response = assistant_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "【提示】用户提问可能与以下表有关：",
                    f"{first_message}",
                    "",
                    "请你调用 Postgres 数据库工具，查询这些的表结构和注释信息。",
                    "最后返回结果中，请注明可用表的表名，以及对应的表结构。不要有无关的文字。",
                ])
            }
        ])
        second_message = second_response[-1].get('content').strip()

        hint = ""
        if len(second_message) > 15:
            hint = "\n".join([
                "可能用到的表，以及对应的表结构如下：",
                f"{second_message}\n\n",
            ])

        # 3. 将相关数据表的 Schema 作为上下文，写入原始查询中
        messages = messages[:-1] + [
            {
                'role': 'user',
                'content': "\n".join([
                    f"当前时间：{now}",
                    "",
                    hint + "用户问题如下：",
                    f"{query}",
                    "",
                    "请你调用 Postgres 数据库查询工具，参考表结构信息，回答用户的问题。",
                ])
            }
        ]

        return messages


if __name__ == '__main__':
    # llm 配置
    llm_cfg = {
        'model': 'Qwen3-0.6B-FP8',
        'model_server': 'http://localhost:8000/v1',
        'api_key': 'token-kcgyrk',
        'generate_cfg': {
            'top_p': 0.95,
            'temperature': 0.6,
        }
    }

    # Postgres 数据库配置
    db_config = {
        "host": "localhost",
        "port": "5432",
        "database": "ecommerce_orders",
        "user": "admin",
        "password": "admin-password",
    }

    # 实例化 PGWorkflow
    pgwf = PGWorkflow(llm_cfg, db_config)

    # 执行 workflow
    query = "请查询用户编号为102的用户的所有订单信息"
    messages = [
        {
            'role': 'user',
            'content': query
        }
    ]
    context = pgwf.workflow(messages)
    print(context)
