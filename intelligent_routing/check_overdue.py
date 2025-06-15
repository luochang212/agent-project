# -*- coding: utf-8 -*-

"""
负责核实物流逾期的路由

写一个用于核查商品是否物流逾期达的 Agent
然后将它封装成 Function Calling
"""

import os
import json
import json5
import psycopg2

from dotenv import load_dotenv
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.agents import Assistant


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


# 外部调用时，使用装饰器配置 llm_cfg
LLM_CFG = dict()


def get_uid_info(uid: int) -> str:
    """获取用户的订单和物流信息"""

    sql = """
    SELECT 
        odr.order_id AS order_id,
        odr.status AS order_status,
        odr.timestamp AS order_timestamp,
        lgs.status AS logistics_status,
        lgs.timestamp AS logistics_timestamp
    FROM
        orders odr
    LEFT JOIN 
        logistics lgs ON odr.order_id = lgs.order_id
    WHERE 
        odr.uid = %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (uid,))

        # 获取所有结果
        records = cursor.fetchall()

        # 如果没有数据
        if not records:
            return ""

        result = [
            "| 订单号 | 订单状态 | 订单时间戳 | 物流状态 | 物流时间戳 |",
            "| --- | --- | --- | --- | --- |"
        ]

        for row in records:
            order_id = str(row[0]) if row[0] is not None else 'NULL'
            order_status = str(row[1]) if row[1] is not None else 'NULL'
            order_timestamp = str(row[2]) if row[2] is not None else 'NULL'
            logistics_status = str(row[3]) if row[3] is not None else 'NULL'
            logistics_timestamp = str(row[4]) if row[4] is not None else 'NULL'

            result.append(
                f"| {order_id} | {order_status} | {order_timestamp} | {logistics_status} | {logistics_timestamp} |"
            )

        return "\n".join(result)


def overdue_checker(uid, bot) -> str:
    """
    确认用户订单是否存在物流逾期的情况

    无论是否逾期，都需要返回结论和对应证据
    """

    # 获取用户的订单物流信息
    user_info = get_uid_info(uid)
    if user_info == '':
        # 用户无订单物流信息
        return ''

    # 判断逾期是否成立，并给出证据
    response = bot.run_nonstream([
        {
            'role': 'user',
            'content': "\n".join([
                "用户的订单物流信息如下：",
                f"{user_info}",
                "",
                "请判断用户订单是否存在物流是否逾期的情况。物流逾期是指：用户下单超过7天，且商品未送达的情况。"
                "请回答订单物流是否逾期的结论和对应的证据。证据需包含具体的时间戳及判断逻辑。",
            ])
        },
    ])
    message = response[-1].get('content').strip()

    return message


def need_retry(final_message, bot):
    """判断是否需要重试"""
    response = bot.run_nonstream([
        {
            'role': 'user',
            'content': "\n".join([
                "以下内容是另一个 Agent 的输出结果：",
                f"{final_message}",
                "",
                "上面这个 Agent 的功能是检查用户订单是否存在物流逾期的情况，并输出结论和对应的证据。",
                "你认为它的回答是否合理且完整。如果合理且完整，回复1，否则回复0，不要回复除数字以外的其他内容。"
            ])
        },
    ])
    message = response[-1].get('content').strip()
    return True if '0' in message else False


def checker(uid: int, llm_cfg: dict, max_retries: int=3) -> str:
    # 初始化 Agent
    bot = Assistant(
        llm=llm_cfg,
        name='物流逾期查询助手',
        description='查询用户订单是否存在物流逾期',
        system_message='',
    )

    for i in range(max_retries):
        if i > 0:
            print(f"启动第 {i} 次复核")

        # 启动核查
        message = overdue_checker(uid, bot)
        if message == '':
            return '该用户无订单物流信息'

        # 判断核查结果是否合理，不合理需要重试
        if not need_retry(message, bot):
            break

    return message


def set_llm_cfg(llm_cfg):
    """装饰器：设置类的llm_cfg属性"""
    def decorator(cls):
        cls.llm_config = llm_cfg
        return cls
    return decorator


@set_llm_cfg(LLM_CFG)
@register_tool('check_overdue')
class OverdueCheckerTool(BaseTool):
    """核查用户的订单是否存在物流逾期的情况"""
    description = (
        '用于查询用户订单是否存在物流逾期，',
        '返回研判结论及证据。'
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
        result = checker(uid, self.llm_config)
        return json.dumps({'result': result}, ensure_ascii=False)


if __name__ == '__main__':
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

    # 为 tool 配置 llm_cfg
    OverdueCheckerTool = set_llm_cfg(llm_cfg)(OverdueCheckerTool)

    # 初始化 Agent
    tools = ['check_overdue']
    bot = Assistant(
        llm=llm_cfg,
        name='逾期查询助手',
        description='查询用户订单物流是否逾期',
        system_message='',
        function_list=tools,
    )

    uid = 102
    messages = [
        {
            'role': 'user',
            'content': f'帮我查一下uid为{uid}的用户，他的订单是否存在物流逾期。请展示逾期或未逾期的证据。'
        },
    ]
    response = bot.run_nonstream(messages)
    print(response)

    # res = overdue_checker(104, bot)
    # print(res)
