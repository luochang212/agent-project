# -*- coding: utf-8 -*-

"""
负责核实用户购买商品是否包含假货的路由

写一个核查用户购买商品是否包含假货的程序
然后将它封装成 Function Calling
"""

import os
import json
import json5
import psycopg2

from dotenv import load_dotenv
from qwen_agent.tools.base import BaseTool, register_tool


# 从 .env 读取数据库配置
load_dotenv()


# 数据库连接
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)


def checker(uid: int) -> str:
    """
    检查用户购买商品中是否存在假货

    如有假货，返回所有假货 goods_id，以逗号分隔
    如无假货，返回空字符串
    """
    sql = """
    SELECT DISTINCT o.goods_id
    FROM orders o
    JOIN fake_goods fg ON o.goods_id = fg.goods_id
    WHERE o.uid = %s
      AND o.status = 'ordered';
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (uid,))

        # 获取所有结果
        records = cursor.fetchall()
        fake_goods = [str(row[0]) for row in records]

    return ','.join(fake_goods)


@register_tool('check_fake_goods')
class FakeGoodsCheckerTool(BaseTool):
    """核查用户的订单中是否存在假货商品"""
    description = (
        '用于查询用户订单中的假货商品。',
        '若用户订单中存在假货商品，返回假货的goods_id列表；否则返回空字符串'
    )
    parameters = [{
        'name': 'uid',
        'type': 'int',
        'description': '用户的uid',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        params_dict = json5.loads(params)
        uid = params_dict['uid']
        result = checker(uid)
        return json.dumps({'result': result}, ensure_ascii=False)


if __name__ == '__main__':
    from qwen_agent.agents import Assistant

    # LLM 配置
    llm_cfg = {
        'model': 'Qwen3-0.6B-FP8',
        'model_server': 'http://localhost:8000/v1',
        'api_key': 'token-kcgyrk',
        'generate_cfg': {
            'top_p': 0.95,
            'temperature': 0.6,
        }
    }

    tools = ['check_fake_goods']

    # 初始化 Agent
    bot = Assistant(
        llm=llm_cfg,
        name='假货查询助手',
        description='查询用户是否买过假货',
        system_message="",
        function_list=tools,
    )

    uid = 103
    messages = [
        {
            'role': 'user',
            'content': f'帮我检查一下uid为{uid}的用户有没有买到假货'
        },
    ]
    response = bot.run_nonstream(messages)
    print(response)

    # res = checker(103)
    # print(res)
