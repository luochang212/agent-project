# 简单的聊天 APP，无 MySQL 查询功能
nohup python gradio_app.py > ./log/gradio_app.log 2>&1 &

# 简单的 MySQL 查询，无 MySQL 定制工作流
nohup python gradio_postgres_agent.py > ./log/gradio_postgres_agent.log 2>&1 &

# 有定制工作流，可以降低查询错误率，但速度较慢
nohup python gradio_postgres_workflow.py > ./log/gradio_postgres_workflow.log 2>&1 &
