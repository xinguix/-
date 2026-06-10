"""
天气查询智能体 - Web 界面
基于 Gradio 4.x + Soft 主题，提供友好的聊天式天气查询体验
"""

import gradio as gr
from weather_agent import agent_executor, safe_encode

# ============================================================
# 常量配置
# ============================================================

CITIES: list[str] = [
    "北京", "上海", "广州", "深圳", "成都",
    "杭州", "武汉", "西安", "南京", "重庆",
]

EXAMPLE_QUERIES: list[tuple[str, str]] = [
    ("🌡️ 实时天气", "北京今天天气怎么样？"),
    ("📅 天气预报", "上海未来几天天气预报"),
    ("🌍 英文查询", "What's the weather in Chengdu today?"),
    ("☔ 出行建议", "深圳今天冷不冷，需要带伞吗？"),
]

# ============================================================
# 自定义 CSS
# ============================================================

CUSTOM_CSS = """
/* ---- 全局 ---- */
.gradio-container { max-width: 100% !important; }

/* ---- 侧边栏区块 ---- */
.sidebar-box {
    background: linear-gradient(135deg, #e8f4fd 0%, #f0f7ff 100%);
    border-radius: 12px;
    padding: 18px 16px;
    margin-bottom: 14px;
    border: 1px solid #d4e6fa;
}
.sidebar-box h3 {
    margin-top: 0; font-size: 15px;
    color: #1a6fb5; font-weight: 600; margin-bottom: 10px;
}

/* ---- 城市快捷按钮 ---- */
.city-btn-row { margin-bottom: 6px; }
.city-btn-row button {
    border-radius: 18px !important;
    font-size: 13px !important;
    padding: 4px 14px !important;
    min-width: 58px !important;
    background: #ffffff !important;
    border: 1.5px solid #b8d8f0 !important;
    color: #2c5f8a !important;
    transition: all 0.2s ease;
}
.city-btn-row button:hover {
    background: #1a6fb5 !important;
    border-color: #1a6fb5 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(26,111,181,0.25);
}
.sidebar-example-btn button {
    text-align: left !important; font-size: 13px !important;
}

/* ---- 主标题 ---- */
.main-header { text-align: center; padding: 10px 0 6px 0; }
.main-header h2 {
    font-size: 26px; font-weight: 700;
    background: linear-gradient(135deg, #1a6fb5, #3da5e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.main-header p { color: #7a8ea0; font-size: 14px; }

/* ---- 聊天窗口 ---- */
#chat-window {
    border-radius: 14px;
    border: 1.5px solid #e2ebf3;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

/* ---- 按钮 ---- */
#submit-btn { border-radius: 10px !important; font-weight: 600 !important; }
#clear-btn { border-radius: 10px !important; color: #888 !important; }

/* ---- 响应式 ---- */
@media (max-width: 768px) {
    .sidebar-box { padding: 10px 8px; }
    .city-btn-row button {
        font-size: 11px !important;
        padding: 2px 8px !important;
        min-width: 44px !important;
    }
}
"""


# ============================================================
# 事件处理函数
# ============================================================


def format_error_message(error: Exception) -> str:
    """将异常转换为用户友好的中文错误信息"""
    error_str = str(error).lower()

    if "timeout" in error_str or "超时" in error_str:
        return "⏱️ 天气服务响应超时，请稍后重试。"
    if "connection" in error_str or "连接" in error_str or "refused" in error_str:
        return "🔌 网络连接失败，请检查网络后重试。"
    if "api key" in error_str or "unauthorized" in error_str or "401" in error_str:
        return "🔑 API 密钥配置有误，请联系管理员。"
    if "rate" in error_str or "429" in error_str:
        return "🚦 请求过于频繁，请稍后重试。"
    return f"❌ 出错了，请稍后重试。（{safe_encode(str(error))}）"


def handle_user_submit(
    message: str, history: list[list[str]]
) -> tuple[str, list[list[str]], dict, dict]:
    """
    用户提交消息的第一阶段：
    1. 添加用户消息和"思考中"占位到聊天记录
    2. 禁用输入框和提交按钮，进入加载状态

    history 格式: [[user_msg, bot_msg], ...]  (Gradio tuples 模式)
    """
    if not message or not message.strip():
        return "", history, gr.update(), gr.update()

    history.append([message.strip(), "🔍 正在查询天气信息，请稍候..."])

    return (
        "",
        history,
        gr.update(interactive=False, placeholder="正在查询..."),
        gr.update(value="⏳ 查询中...", interactive=False),
    )


def handle_bot_respond(
    history: list[list[str]],
) -> tuple[list[list[str]], dict, dict]:
    """
    用户提交消息的第二阶段（.then 链式调用）：
    调用 Agent，用真实回答替换"思考中"占位
    """
    if not history:
        return history, gr.update(), gr.update()

    try:
        # 取最后一条用户消息作为 agent 输入
        last_user_msg = history[-1][0]

        # 将 history 转为 langchain messages 格式（去掉最后一条占位）
        messages: list[dict] = []
        for user_msg, bot_msg in history[:-1]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

        result = agent_executor.invoke({
            "input": last_user_msg,
            "chat_history": messages,
        })
        answer = safe_encode(result["output"])

        # 替换占位消息
        history[-1][1] = answer

        return (
            history,
            gr.update(interactive=True, placeholder="输入你想查询的城市和天气..."),
            gr.update(value="查询天气", interactive=True),
        )

    except Exception as e:
        history[-1][1] = format_error_message(e)
        return (
            history,
            gr.update(interactive=True, placeholder="输入你想查询的城市和天气..."),
            gr.update(value="查询天气", interactive=True),
        )


def make_fill_handler(text: str):
    """工厂函数：用闭包捕获文本值，避免使用 gr.State"""
    return lambda: text


def clear_conversation() -> tuple[list, str, dict, dict]:
    """清空对话，恢复 UI 状态"""
    return (
        [],
        "",
        gr.update(interactive=True, placeholder="输入你想查询的城市和天气..."),
        gr.update(value="查询天气", interactive=True),
    )


# ============================================================
# 构建 Gradio 界面
# ============================================================

theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.sky,
    neutral_hue=gr.themes.colors.slate,
    font=gr.themes.GoogleFont("Noto Sans SC"),
).set(
    body_background_fill="*neutral_50",
    block_background_fill="white",
    block_border_width="0px",
    block_radius="12px",
    button_primary_background_fill="#1a6fb5",
    button_primary_background_fill_hover="#155b95",
    button_shadow="*shadow_drop_lg",
)


with gr.Blocks(
    theme=theme,
    css=CUSTOM_CSS,
    title="天气查询助手",
) as demo:

    # ---- 顶部标题 ----
    gr.HTML("""
    <div class="main-header">
        <h2>🌤️ 天气查询智能助手</h2>
        <p>基于通义千问 + 高德地图天气 API · 支持中英文查询</p>
    </div>
    """)

    # ---- 双栏布局 ----
    with gr.Row(equal_height=False):

        # ========== 左侧边栏 ==========
        with gr.Column(scale=1, min_width=220):

            with gr.Group(elem_classes="sidebar-box"):
                gr.Markdown("### 🏙️ 常用城市")
                city_buttons: list[tuple[gr.Button, str]] = []
                for i in range(0, len(CITIES), 2):
                    with gr.Row(elem_classes="city-btn-row"):
                        for city in CITIES[i:i + 2]:
                            btn = gr.Button(city, size="sm", min_width=64)
                            city_buttons.append((btn, city))

            with gr.Group(elem_classes="sidebar-box"):
                gr.Markdown("### 💡 试试这些")
                example_buttons: list[tuple[gr.Button, str]] = []
                for label, query in EXAMPLE_QUERIES:
                    btn = gr.Button(label, size="sm", elem_classes="sidebar-example-btn")
                    example_buttons.append((btn, query))

            with gr.Group(elem_classes="sidebar-box"):
                gr.Markdown("""
                **📌 提示**
                - 支持全国主要城市
                - 可查询实时天气 / 未来预报
                - 中英文均可
                """)

        # ========== 右侧主聊天区 ==========
        with gr.Column(scale=4):

            chatbot = gr.Chatbot(
                value=[],
                label="",
                height=480,
                bubble_full_width=False,
                show_copy_button=True,
                avatar_images=(
                    None,
                    "https://cdn-icons-png.flaticon.com/512/1005/1005141.png",
                ),
                placeholder="你好！我是天气查询助手，请输入你想查询的城市和天气信息...",
                elem_id="chat-window",
            )

            msg = gr.Textbox(
                label="",
                placeholder="例如：北京今天天气怎么样？",
                lines=2,
                max_lines=4,
                show_label=False,
            )

            with gr.Row():
                submit_btn = gr.Button(
                    "查询天气",
                    variant="primary",
                    scale=2,
                    elem_id="submit-btn",
                )
                clear_btn = gr.Button(
                    "清空对话",
                    variant="secondary",
                    scale=1,
                    elem_id="clear-btn",
                )

    # ============================================================
    # 事件绑定
    # ============================================================

    submit_ins = [msg, chatbot]
    submit_outs = [msg, chatbot, msg, submit_btn]
    respond_outs = [chatbot, msg, submit_btn]

    # ---- 提交按钮 ----
    submit_evt = submit_btn.click(
        fn=handle_user_submit, inputs=submit_ins, outputs=submit_outs, queue=True
    )
    submit_evt.then(
        fn=handle_bot_respond, inputs=[chatbot], outputs=respond_outs, queue=True
    )

    # ---- 回车提交 ----
    enter_evt = msg.submit(
        fn=handle_user_submit, inputs=submit_ins, outputs=submit_outs, queue=True
    )
    enter_evt.then(
        fn=handle_bot_respond, inputs=[chatbot], outputs=respond_outs, queue=True
    )

    # ---- 清空对话 ----
    clear_btn.click(
        fn=clear_conversation,
        inputs=[],
        outputs=[chatbot, msg, msg, submit_btn],
        queue=False,
    )

    # ---- 城市快捷按钮 ----
    for btn, city in city_buttons:
        btn.click(
            fn=make_fill_handler(f"{city}今天天气怎么样？"),
            inputs=[],
            outputs=[msg],
            queue=False,
        ).then(
            fn=handle_user_submit,
            inputs=submit_ins,
            outputs=submit_outs,
            queue=True,
        ).then(
            fn=handle_bot_respond,
            inputs=[chatbot],
            outputs=respond_outs,
            queue=True,
        )

    # ---- 示例问题按钮 ----
    for btn, query in example_buttons:
        btn.click(
            fn=make_fill_handler(query),
            inputs=[],
            outputs=[msg],
            queue=False,
        ).then(
            fn=handle_user_submit,
            inputs=submit_ins,
            outputs=submit_outs,
            queue=True,
        ).then(
            fn=handle_bot_respond,
            inputs=[chatbot],
            outputs=respond_outs,
            queue=True,
        )


if __name__ == "__main__":
    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False,
    )
