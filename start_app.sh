# 简单的聊天 APP，无 SQL 查询功能
nohup python gradio_app.py > ./log/gradio_app.log 2>&1 &

# [Agent] 简单查询，无定制工作流
nohup python gradio_postgres_agent.py > ./log/gradio_postgres_agent.log 2>&1 &

# [Workflow] 定制工作流，可以降低错误率，但查询速度较慢
nohup python gradio_postgres_workflow.py > ./log/gradio_postgres_workflow.log 2>&1 &
