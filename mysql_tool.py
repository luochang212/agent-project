# -*- coding: utf-8 -*-

"""
MySQL 数据库的 Qwen-Agent Function Calling 模块 

主要工具：
- TableInfoTool: 获取数据库所有表及其注释信息
- ColumnsInfoTool: 获取指定表的字段定义和注释
- SampleDataTool: 获取表的随机样例数据
- EnumValuesTool: 获取字段的枚举值统计
"""

import json
import json5

from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from mysql_client import (get_table_info as mysql_get_table_info,
                          get_table_columns_info as mysql_get_columns_info,
                          get_random_sample as mysql_get_sample,
                          get_top_enum_values as mysql_get_enum_values,
                          load_env, create_conn_from_dotenv, close_conn)


# 加载数据库配置
# db_config = load_env()  # 从 .env 文件中加载
db_config = dict()  # 未来使用 set_db_config 函数加载


def set_db_config(config: dict):
    """更新数据库配置"""
    global db_config
    db_config.update(config)


@register_tool('get_table_info')
class TableInfoTool(BaseTool):
    """获取数据库所有表及其注释信息"""
    description = '查询数据库中的所有表及其表注释信息'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        conn = create_conn_from_dotenv(db_config)
        try:
            result = mysql_get_table_info(conn)
            return json.dumps({'result': result}, ensure_ascii=False)
        finally:
            close_conn(conn)


@register_tool('get_table_columns_info')
class ColumnsInfoTool(BaseTool):
    """获取指定表的字段定义和注释"""
    description = '查询指定表的所有字段定义和注释信息'
    parameters = [{
        'name': 'table_name',
        'type': 'string',
        'description': '需要查询的表名',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        conn = create_conn_from_dotenv(db_config)
        try:
            params_dict = json5.loads(params)
            table_name = params_dict['table_name']
            result = mysql_get_columns_info(conn, table_name)
            return json.dumps({'result': result}, ensure_ascii=False)
        finally:
            close_conn(conn)


@register_tool('get_random_sample')
class SampleDataTool(BaseTool):
    """获取表的随机样例数据"""
    description = '查询指定表的随机样例数据'
    parameters = [{
        'name': 'table_name',
        'type': 'string',
        'description': '需要查询的表名',
        'required': True
    }, {
        'name': 'columns',
        'type': 'array',
        'description': '需要查询的字段列表，如果不指定则查询所有字段',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        conn = create_conn_from_dotenv(db_config)
        try:
            params_dict = json5.loads(params)
            table_name = params_dict['table_name']
            columns = params_dict.get('columns', None)
            result = mysql_get_sample(conn, table_name, columns)
            return json.dumps({'result': result}, ensure_ascii=False)
        finally:
            close_conn(conn)


@register_tool('get_top_enum_values')
class EnumValuesTool(BaseTool):
    """获取字段的枚举值统计"""
    description = '查询指定字段出现频率最高的前 N 个枚举值'
    parameters = [{
        'name': 'table_name',
        'type': 'string',
        'description': '需要查询的表名',
        'required': True
    }, {
        'name': 'column_name',
        'type': 'string',
        'description': '需要统计的字段名',
        'required': True
    }, {
        'name': 'limit',
        'type': 'integer',
        'description': '返回的结果数量，默认为 10',
        'default': 10
    }]

    def call(self, params: str, **kwargs) -> str:
        conn = create_conn_from_dotenv(db_config)
        try:
            params_dict = json5.loads(params)
            table_name = params_dict['table_name']
            column_name = params_dict['column_name']
            limit = params_dict.get('limit', 10)
            result = mysql_get_enum_values(conn, table_name, column_name, limit)
            return json.dumps({'result': result}, ensure_ascii=False)
        finally:
            close_conn(conn)


if __name__ == '__main__':
    # 创建 Agent
    llm_cfg = {
        'model': 'Qwen3-0.6B-FP8',
        'model_server': 'http://localhost:8000/v1',
        'api_key': 'token-kcgyrk',
        'generate_cfg': {
            'top_p': 0.95,
            'temperature': 0.6,
        }
    }

    # 配置数据库参数
    set_db_config({
        "host": "localhost",
        "port": 3306,
        "database": "score",
        "user": "admin",
        "password": "admin-password",
        "charset": "utf8mb4",
    })

    system_prompt = """
    你是一个数据库查询助手，专门帮助用户查询和分析 MySQL 数据库中的数据。
    规则：
    1. 始终确保 SQL 查询的安全性，避免修改数据
    2. 以清晰易懂的方式呈现查询结果
    3. 当用户询问数据库结构时，优先使用表信息和字段信息工具
    4. 当用户需要了解数据内容时，使用样例数据工具
    5. 当用户询问某个字段的取值情况时，使用枚举值统计工具
    """

    tools = ['get_table_info', 'get_table_columns_info', 'get_random_sample', 'get_top_enum_values']
    bot = Assistant(
        llm=llm_cfg,
        name='MySQL数据库查询助手',
        description='帮助用户查询 MySQL 数据库',
        system_message=system_prompt,
        function_list=tools,
    )

    # 测试示例
    query = '数据库中有哪些表？'
    messages = [{'role': 'user', 'content': query}]

    response = bot.run_nonstream(messages)
    print("=== 查询数据库表信息 ===")
    print(response)

    # 测试查询表结构
    query2 = '请查看 students 表的字段信息'
    messages2 = [{'role': 'user', 'content': query2}]

    response2 = bot.run_nonstream(messages2)
    print("\n=== 查询表字段信息 ===")
    print(response2)

    # 测试查询样例数据
    query3 = '请查看 students 表的样例数据'
    messages3 = [{'role': 'user', 'content': query3}]

    response3 = bot.run_nonstream(messages3)
    print("\n=== 查询表样例数据 ===")
    print(response3)
