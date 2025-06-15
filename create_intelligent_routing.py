# -*- coding: utf-8 -*-

"""
创建智能路由
"""

from intelligent_routing.agent import workflow


# 客诉内容
complaint = {
    "time": "2025-06-10",
    "uid": 103,
    "content": "等了很久，没收到货"
}


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


res = workflow(complaint, llm_cfg)
print(res)
