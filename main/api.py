"""
天气查询智能体 - Web 界面
使用 Gradio 创建友好的网页前端
"""
import gradio as gr
from weather_agent import agent_executor  # 导入智能体执行器

def weather_chat(message, history):
    """
    处理用户的天气查询请求
    """
    # 确保 history 是正确的格式（列表的列表）
    if history is None:
        history = []
    
    try:
        # 将历史对话转换为 messages 格式
        messages = []
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": message})
        
        # 调用智能体，传递完整的聊天历史
        result = agent_executor.invoke({
            "input": message,
            "chat_history": messages
        })
        answer = result["output"]
        # 处理编码问题
        answer = answer.encode('utf-8', 'replace').decode('utf-8')
        # Gradio 4.x 需要列表格式，不是元组
        new_history = history + [[message, answer]]
        return new_history
    except Exception as e:
        error_msg = f"❌ 出错了: {str(e)}"
        new_history = history + [[message, error_msg]]
        return new_history

# 创建 Gradio 界面
with gr.Blocks(title="🌤️ 天气查询助手") as demo:
    gr.Markdown("""
    # 🌤️ 天气查询智能助手
    
    基于 **通义千问** + **高德地图天气 API** 构建的智能天气查询助手。
    
    **支持的功能：**
    - 🌡️ 实时天气查询（温度、湿度、风向风力等）
    - 📅 未来3-4天天气预报
    - 🌍 支持全国主要城市
    - 🌐 支持中英文查询
    
    **示例问题：**
    - "北京今天天气怎么样？"
    - "上海未来几天的天气预报"
    - "What's the weather in Chengdu today?"
    - "成都今天冷不冷？"
    """)
    
    # 聊天界面
    chatbot = gr.Chatbot(
        height=500,
        bubble_full_width=False,
        avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/1005/1005141.png"),
    )
    
    # 输入框
    msg = gr.Textbox(
        label="输入你的问题",
        placeholder="例如：北京今天天气怎么样？",
        lines=2,
    )
    
    # 按钮
    with gr.Row():
        submit_btn = gr.Button("查询天气", variant="primary")
        clear_btn = gr.Button("清空对话")
    
    # 设置交互
    submit_btn.click(
        weather_chat,
        inputs=[msg, chatbot],
        outputs=chatbot,
    ).then(lambda: gr.update(value=""), None, msg)
    
    msg.submit(
        weather_chat,
        inputs=[msg, chatbot],
        outputs=chatbot,
    ).then(lambda: gr.update(value=""), None, msg)
    
    clear_btn.click(
        lambda: None,
        None,
        chatbot,
        queue=False,
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )