# -*- coding: utf-8 -*-

"""
Gradio 聊天界面

定义聊天界面的样式，通过 `generate_response` 函数模拟大语言模型的回复。
"""

import gradio as gr
import random
import time


# 模拟大语言模型生成回复
def generate_response(message, history):
    if not message.strip():
        return message, history

    # 模拟大语言模型处理延迟
    processing_time = random.uniform(0.5, 1.5)
    time.sleep(processing_time)

    # 模拟生成智能回复
    responses = [
        "这是一个基于大语言模型的回复示例。",
        "我理解你的查询了。",
        "感谢你的提问！"
    ]

    # 使用新的消息格式
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": random.choice(responses)})
    return "", history


# 自定义 CSS 样式
custom_css = """
:root {
    --primary: #007AFF;
    --secondary: #0066CC;
    --dark: #1C1C1E;
    --light: #F2F2F7;
    --gray: #E5E5EA;
}

.dark .gradio-container {
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.layout {
    border-radius: 20px !important;
    overflow: hidden !important;
    background: white !important;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

/* 输入区域样式 */
.input-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1rem;
    background: #0b0f19;
    margin-top: auto;
}

/* 文本框样式 */
.textbox {
    flex: 1 1 auto;
    max-width: calc(100% - 100px);
    border-radius: 24px !important;
    padding: 12px 24px !important;
    background: dark !important;
    color: var(--dark) !important;
    font-size: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease !important;
}

/* 焦点效果 */
.textbox:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2) !important;
}

/* 按钮样式 */
.button {
    flex: 0 0 auto;
    height: 45px;
    min-width: 80px;
    padding: 0 20px;
    border-radius: 24px !important;
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2) !important;
}

/* 悬停效果 */
.button:hover {
    background: var(--secondary) !important;
    box-shadow: 0 6px 16px rgba(0, 122, 255, 0.3) !important;
}

/* 点击效果 */
.button:active {
    transform: scale(0.98);
}

/* 对话框样式统一 */
.user, .assistant {
    background: var(--primary) !important;
    color: white !important;
    margin-left: auto !important;
    border-radius: 16px !important;
    padding: 12px 16px !important;
    max-width: 80%;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
    .textbox {
        padding: 10px 16px !important;
        font-size: 14px !important;
    }
    
    .button {
        min-width: 60px;
        padding: 0 12px;
        font-size: 14px;
    }
}
"""

def create_ui(llm_func):
    """创建聊天界面"""
    with gr.Blocks(
        title="LLM Chat Interface",
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="blue"),
        css=custom_css
    ) as ui:
        # 标题区域
        gr.Markdown(
            """
            # <center>🤖 大语言模型对话系统</center>
            <center><font size=3>基于 Gradio 构建的现代聊天界面</font></center>
            """,
            elem_classes=["dark"]
        )
        
        # 聊天区域
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            type="messages",
            avatar_images=(
                None,  # 用户头像
                None   # AI头像
            ),
            height=600,
            elem_classes=["dark"]
        )

        # 输入区域 - 添加新的样式类
        with gr.Row(elem_classes=["input-row", "dark"]) as input_row:
            msg = gr.Textbox(
                placeholder="输入消息...",
                show_label=False,
                container=False,
                elem_classes=["textbox", "dark"]
            )
            submit_btn = gr.Button("发送", elem_classes=["button"])

        # 交互逻辑
        def clear_input():
            return ""

        msg.submit(
            llm_func,
            [msg, chatbot],
            [msg, chatbot]
        )
        
        submit_btn.click(
            llm_func,
            [msg, chatbot],
            [msg, chatbot]
        )
    
    return ui


if __name__ == "__main__":
    demo = create_ui(llm_func=generate_response)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False
    )
