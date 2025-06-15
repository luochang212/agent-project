# -*- coding: utf-8 -*-

"""
客诉核查 Agent
"""

from qwen_agent.agents import Assistant

from .check_fake_goods import FakeGoodsCheckerTool
from .check_overdue import set_llm_cfg, OverdueCheckerTool


def workflow(complaint, llm_cfg):
    """客诉核查工作流"""

    # 修改 check_overdue 的 llm_cfg
    global OverdueCheckerTool
    OverdueCheckerTool = set_llm_cfg(llm_cfg)(OverdueCheckerTool)

    # 1. 判断客诉类型，以及是否在处理范围内

    # 护栏 Agent：处理无法解决的客诉类型
    guardrails_bot = Assistant(
        llm=llm_cfg,
        name='护栏 Agent',
        description='客诉类型判断',
    )

    messages = [
        {
            'role': 'user',
            'content': "\n".join([
                "客诉信息如下：",
                f"{complaint['content']}",
                "",
                "系统只能处理两种客诉：物流逾期、假货。请判断客诉是否属于哪种问题。",
                "如果是物流逾期，回复1；如果是假货，回复2；明确属于物流和假货之外的其他问题的，回复3；不清楚属于哪种类型的，回复4。",
                "请只回答数字，不要回复多余的文字。"
            ])
        },
    ]
    first_response = guardrails_bot.run_nonstream(messages)
    first_message = first_response[-1].get('content').strip()

    response = '护栏 Agent：从客诉内容判断是{}问题。'
    if '1' in first_message:
        print(response.format('物流逾期'))
    elif '2' in first_message:
        print(response.format('假货'))
    elif '3' in first_message:
        return '系统无法处理该客诉，任务结束'
    elif '4' in first_message:
        print(response.format('不清楚是什么'))
    else:
        print(f'Warning: 护栏 Agent 似乎有异常，它的输出为：{first_message}')


    # 2. 判断客诉是否成立，并给出证据

    # 客诉判定 Agent：调用工具判定客诉是否属实
    tools = ['check_fake_goods', 'check_overdue']
    judge_bot = Assistant(
        llm=llm_cfg,
        name='客诉判定 Agent',
        description='用于判定客诉是否属实',
        system_message='',
        function_list=tools,
    )

    messages = [
        {
            'role': 'user',
            'content': "\n".join([
                "客诉信息如下：",
                f"- 投诉时间：{complaint['time']}",
                f"- 投诉用户的uid：{complaint['uid']}",
                f"- 投诉内容：{complaint['content']}",
                "",
                "请调用工具判断客诉内容是否属实。"
                "无论是否属实，请给出客诉类型，研判结论、以及支持该研判结论的证据。",
                "客诉类型限定为：物流逾期、假货、其他。"
            ])
        },
    ]
    second_response = judge_bot.run_nonstream(messages)
    second_message = second_response[-1].get('content').strip()
    return second_message
