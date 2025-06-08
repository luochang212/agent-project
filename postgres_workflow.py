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

import postgres_tool

from qwen_agent.agents import Assistant, ReActChat


SYSTEM_PROMPT = """
你是一个数据库查询助手，专门帮助用户查询和分析 PostgreSQL 数据库中的数据。

规则：
1. 始终确保 SQL 查询的安全性，避免修改数据
2. 以清晰易懂的方式呈现查询结果
"""

import postgres_tool

from qwen_agent.agents import Assistant, ReActChat


class PGWorkflow:

    def __init__(self, llm_cfg, db_config=None):
        self.llm_cfg = llm_cfg
        self.db_config = db_config
        self.agents = dict()

    def set_db_config(self):
        if self.db_config is None:
            print("Warning: self.db_config is None")
        else:
            postgres_tool.set_db_config(self.db_config)

    def create_pg_agent(self):
        """用来执行最终查询的 Agent，使用 ReActChat 模式"""
        pg_tools = [{
          "mcpServers": {
            "postgres": {
              "command": "npx",
              "args": [
                "-y",
                "@modelcontextprotocol/server-postgres",
                "postgresql://admin:admin-password@localhost:5432/ecommerce_orders",
                "--introspect"  # 自动读取数据库模式
              ]
            }
          }
        }]

        return ReActChat(
            llm=self.llm_cfg,
            name='Postgres 数据库助手',
            description='使用 ReAct 模式查询 Postgres 数据库',
            system_message=SYSTEM_PROMPT,
            function_list=pg_tools,
        )

    def create_fn_agent(self):
        """为最终查询提供数据库和数据表信息的 Agent"""
        func_tools = [
            'get_table_info',
            'get_table_columns_info',
            'get_random_sample',
            'get_top_enum_values'
        ]

        return Assistant(
            llm=self.llm_cfg,
            name='Agent 数据库查询助手',
            description='帮助 Agent 查询 PostgreSQL 数据库元信息',
            system_message=SYSTEM_PROMPT,
            function_list=func_tools,
        )

    def register(self):
        """创建并注册 Agent"""
        self.agents = {
            'pg': self.create_pg_agent(),
            'fn': self.create_fn_agent(),
        }

    def workflow(self, query):
        """定制的 Postgres 数据库查询流程，用来增加查询成功率"""
        # 配置 Postgres 数据库（如需）
        self.set_db_config()

        # 注册本 workflow 所需 Agent
        self.register()

        pg_bot = self.agents['pg']
        fn_bot = self.agents['fn']
        

        # 1. 定位数据表
        first_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "你不需要回答用户提问。你需要：",
                    "1. 查询 Postgres 数据库中有哪些表",
                    "2. 回答用户提问中可能用到其中哪些表",
                    "注意，最终返回结果中，只需要包含你认为可能用到的表。如你认为没有可能用到的表，回答无可用表",
                ])
            }
        ])

        # 2. 查询表结构
        first_message = first_response[-1].get('content').strip()
        second_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "上一个Agent认为可能用到的表如下：",
                    f"{first_message}",
                    "请你调用 Postgres 数据库助手，查询可能用到的表的表结构",
                    "回答可能用到的表的表名，以及该表的表结构",
                ])
            }
        ])

        # 3. 将以上内容作为上下文，注入原始查询中
        second_message = second_response[-1].get('content').strip()
        third_response = pg_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "可能用到的表，以及该表的表结构如下：",
                    f"{second_message}",
                    "请你调用 Postgres 数据库助手，参考表结构信息，回答用户的提问",
                ])
            }
        ])
        third_message = third_response[-1].get('content').strip()

        # ReAct 模式需获取 'Final Answer: ' 之后的内容作为回答
        if 'Final Answer: ' in third_message:
            return third_message.split('Final Answer: ')[-1]

        return third_message


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

    # 实例化 Workflow
    pgwf = PGWorkflow(llm_cfg, db_config)

    # 执行优化 SQL 查询的 workflow
    query = "请在订单表中查询用户编号为102的用户的所有订单信息"
    answer = pgwf.workflow(query)
    print(answer)
