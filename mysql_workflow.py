# -*- coding: utf-8 -*-

"""
定制的 MySQL 数据库查询流程，增加查询成功率

主要步骤：
1. 确认需要用到的数据表
2. 查询可能用到的表和表结构
3. 将表名和表结构作为上下文，注入原始查询

适用性：
  只接受需要用到一张表的情况，如果需要多张表和表结构，需要额外开发
"""

import mysql_tool

from qwen_agent.agents import Assistant


SYSTEM_PROMPT = """
你是一个数据库查询助手，专门帮助用户查询和分析 MySQL 数据库中的数据。

规则：
1. 始终确保 SQL 查询的安全性，避免修改数据
2. 以清晰易懂的方式呈现查询结果
3. 当用户询问数据库结构时，优先使用表信息和字段信息工具
4. 当用户需要了解数据内容时，使用样例数据工具
5. 当用户询问某个字段的取值情况时，使用枚举值统计工具
"""


class MySQLWorkflow:

    def __init__(self, llm_cfg, db_config=None):
        self.llm_cfg = llm_cfg
        self.db_config = db_config
        self.agents = dict()

    def set_db_config(self):
        """设置数据库配置"""
        if self.db_config is None:
            print("Warning: self.db_config is None")
        else:
            mysql_tool.set_db_config(self.db_config)

    def create_mysql_agent(self):
        """用来执行最终查询的 Agent，使用 Assistant 模式"""
        mysql_tools = [
            'get_table_info',
            'get_table_columns_info',
            'get_random_sample',
            'get_top_enum_values'
        ]

        return Assistant(
            llm=self.llm_cfg,
            name='MySQL 数据库助手',
            description='查询 MySQL 数据库并执行 SQL 查询',
            system_message=SYSTEM_PROMPT,
            function_list=mysql_tools,
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
            description='帮助 Agent 查询 MySQL 数据库元信息',
            system_message=SYSTEM_PROMPT,
            function_list=func_tools,
        )

    def register(self):
        """创建并注册 Agent"""
        self.agents = {
            'mysql': self.create_mysql_agent(),
            'fn': self.create_fn_agent(),
        }

    def workflow(self, query):
        """定制的 MySQL 数据库查询流程，用来增加查询成功率"""
        # 配置 MySQL 数据库（如需）
        self.set_db_config()

        # 注册本 workflow 所需 Agent
        self.register()

        mysql_bot = self.agents['mysql']
        fn_bot = self.agents['fn']
        

        # 1. 定位数据表
        first_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "你不需要回答用户提问。你需要：",
                    "1. 查询 MySQL 数据库中有哪些表",
                    "2. 回答用户提问中可能用到其中哪些表",
                    "注意，最终返回结果中，只需要包含你认为可能用到的表。如你认为没有可能用到的表，回答无可用表",
                ])
            }
        ])

        # 2. 查询表结构和样例数据
        first_message = first_response[-1].get('content').strip()
        second_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "上一个Agent认为可能用到的表如下：",
                    f"{first_message}",
                    "请你调用 MySQL 数据库助手，查询可能用到的表的详细信息，包括：",
                    "1. 表的字段结构和注释",
                    "2. 表的样例数据（少量即可）",
                    "回答可能用到的表的表名，字段结构，以及样例数据",
                ])
            }
        ])

        # 3. 将以上内容作为上下文，注入原始查询中
        second_message = second_response[-1].get('content').strip()
        third_response = mysql_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "可能用到的表，以及该表的字段结构和样例数据如下：",
                    f"{second_message}",
                    "请你参考表结构和样例数据信息，回答用户的提问。",
                    "如果需要执行 SQL 查询，请使用提供的数据库工具来获取相关信息。",
                ])
            }
        ])
        third_message = third_response[-1].get('content').strip()

        return third_message

    def workflow_with_sql_execution(self, query):
        """
        带 SQL 执行能力的工作流程
        注意：需要额外的 SQL 执行工具支持
        """
        # 配置 MySQL 数据库（如需）
        self.set_db_config()

        # 注册本 workflow 所需 Agent
        self.register()

        mysql_bot = self.agents['mysql']
        fn_bot = self.agents['fn']
        

        # 1. 定位数据表
        first_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "用户提问如下：",
                    f"{query}",
                    "你不需要回答用户提问。你需要：",
                    "1. 查询 MySQL 数据库中有哪些表",
                    "2. 分析用户提问中可能用到其中哪些表",
                    "注意，最终返回结果中，只需要包含你认为可能用到的表名。如你认为没有可能用到的表，回答无可用表",
                ])
            }
        ])

        # 2. 查询表结构和样例数据
        first_message = first_response[-1].get('content').strip()
        
        if "无可用表" in first_message:
            return "抱歉，根据您的查询，我无法在数据库中找到相关的表。请检查您的查询内容或联系管理员确认数据库结构。"
        
        second_response = fn_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "上一步识别的可能用到的表如下：",
                    f"{first_message}",
                    "请你：",
                    "1. 查询这些表的字段结构和注释信息",
                    "2. 获取这些表的样例数据（每个表获取少量数据即可）",
                    "3. 如果表中有枚举类型的字段，获取该字段的常见取值",
                    "请详细返回表结构、字段说明和样例数据信息",
                ])
            }
        ])

        # 3. 基于表结构信息回答用户查询
        second_message = second_response[-1].get('content').strip()
        third_response = mysql_bot.run_nonstream([
            {
                'role': 'user',
                'content': "\n".join([
                    "原始用户提问：",
                    f"{query}",
                    "",
                    "数据库表结构和样例数据信息：",
                    f"{second_message}",
                    "",
                    "请基于以上表结构和样例数据信息，回答用户的提问。",
                    "如果需要查询具体数据，请使用适当的数据库查询工具。",
                    "请确保您的回答准确、完整，并符合数据库中的实际数据结构。",
                ])
            }
        ])
        third_message = third_response[-1].get('content').strip()

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

    # MySQL 数据库配置
    db_config = {
        "host": "localhost",
        "port": 3306,
        "database": "score",
        "user": "admin",
        "password": "admin-password",
        "charset": "utf8mb4",
    }

    # 实例化 Workflow
    mysql_wf = MySQLWorkflow(llm_cfg, db_config)

    # 执行优化 SQL 查询的 workflow
    query = "请查询学生表中学号为1001的学生的所有信息"
    answer = mysql_wf.workflow_with_sql_execution(query)
    print("=== MySQL Workflow 执行结果 ===")
    print(answer)

    # 测试多个查询
    test_queries = [
        "数据库中有多少个学生？",
        "显示成绩最高的5个学生信息",
        "查询平均分超过80分的学生名单",
    ]

    for test_query in test_queries:
        print(f"\n=== 测试查询: {test_query} ===")
        result = mysql_wf.workflow_with_sql_execution(test_query)
        print(result)
