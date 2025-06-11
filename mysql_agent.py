# -*- coding: utf-8 -*-

"""
定制的 MySQL 数据库查询流程，增加查询成功率

主要步骤：
1. 确认需要用到的数据表
2. 查询可能用到的表和表结构
3. 将表名和表结构作为上下文，注入原始查询
"""

import mysql_tool

from qwen_agent.agents import Assistant, ReActChat


SYSTEM_PROMPT = """
你是一个数据库查询助手，专门帮助用户查询和分析 MySQL 数据库中的数据。

规则：
1. 始终确保 SQL 查询的安全性，避免修改数据
2. 以清晰易懂的方式呈现查询结果
3. 当用户询问数据库结构时，优先使用表信息和字段信息工具
4. 当用户需要了解数据内容时，使用样例数据工具
5. 当用户询问某个字段的取值情况时，使用枚举值统计工具
"""


class MySQLAgent:
    """MySQL Agent"""

    def __init__(self, llm_cfg, db_config=None):
        self.llm_cfg = llm_cfg

        # MySQL 数据库配置
        # 允许 db_config 为 None，为 None 时使用 .env 中的配置
        self.db_config = db_config
        self.set_db_config()

    def set_db_config(self):
        """设置数据库配置"""
        if self.db_config is None:
            print("Warning: self.db_config is None")
        else:
            mysql_tool.set_db_config(self.db_config)

    def create_tools(self):
        """获取工具列表"""

        # MySQL 数据库配置
        host = self.db_config.get('host')
        port = self.db_config.get('port')
        db = self.db_config.get('database')
        user = self.db_config.get('user')
        password = self.db_config.get('password')

        # 工具列表
        tools = [
            {
                "mcpServers": {
                    "mysql": {
                        "type": "stdio",
                        "command": "uvx",
                        "args": [
                            "--from",
                            "mysql-mcp-server",
                            "mysql_mcp_server"
                        ],
                        "env": {
                            "MYSQL_HOST": host,
                            "MYSQL_PORT": str(port),
                            "MYSQL_USER": user,
                            "MYSQL_PASSWORD": password,
                            "MYSQL_DATABASE": db
                        }
                    }
                }
            },
            'get_table_info',
            'get_table_columns_info',
            'get_random_sample',
            'get_top_enum_values',
        ]

        return tools

    def create_react_agent(self):
        """创建 ReActChat 模式的 Agent"""
        tools = self.create_tools()
        return ReActChat(
            llm=self.llm_cfg,
            name='MySQL 数据库助手',
            description='使用 ReActChat 模式查询 MySQL 数据库',
            system_message=SYSTEM_PROMPT,
            function_list=tools,
        )

    def create_assistant_agent(self):
        """创建 Assistant 模式的 Agent"""
        tools = self.create_tools()
        return Assistant(
            llm=self.llm_cfg,
            name='MySQL 数据库助手',
            description='使用 Assistant 模式查询 MySQL 数据库',
            system_message=SYSTEM_PROMPT,
            function_list=tools,
        )

    def ask(self, bot, messages: list) -> str:
        """使用指定的 bot 进行查询"""
        response = bot.run_nonstream(messages)
        message = response[-1].get('content').strip()
        return message


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

    # MySQL 数据库配置
    db_config = {
        "host": "localhost",
        "port": 3306,
        "database": "score",
        "user": "admin",
        "password": "admin-password",
    }

    # 实例化 MySQLAgent
    msa = MySQLAgent(llm_cfg, db_config)

    # 创建一个 Agent
    react_agent = msa.create_react_agent()
    # assistant_agent = msa.create_assistant_agent()

    # 使用 Agent 查询 MySQL 数据库
    query = "查询学号为1001的学生的信息"
    messages = [
        {
            'role': 'user',
            'content': query
        }
    ]
    answer = msa.ask(react_agent, messages)
    print(answer)
