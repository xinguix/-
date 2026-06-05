"""
天气查询智能体 - FastAPI 接口
启动后访问 http://127.0.0.1:8000/docs 即可测试
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from weather_agent import agent   # 导入你已创建好的智能体

# 创建 FastAPI 应用
app = FastAPI(
    title="🌤️ 天气查询助手 API",
    description="基于通义千问 + 高德天气的智能助手，支持实时天气和未来天气预报",
    version="1.0.0",
)

# 定义请求体模型
class WeatherQuery(BaseModel):
    question: str = Field(
        ...,
        description="你的天气问题，例如：'北京今天天气怎么样？' 或 '上海未来几天天气预报'",
        example="成都今天天气怎么样"
    )

# 定义响应体模型（可选，但能让文档更清晰）
class WeatherResponse(BaseModel):
    answer: str = Field(..., description="智能助手的回复内容")

@app.post("/weather", response_model=WeatherResponse, summary="天气查询")
async def ask_weather(query: WeatherQuery):
    """
    输入你的天气问题，智能助手将调用实时天气或预报工具，返回人性化的答案。

    - **question**: 用自然语言描述你想查询的城市和天气类型
    """
    # 调用智能体
    result = agent.invoke({
        "messages": [{"role": "user", "content": query.question}]
    })
    # 提取最后一条 AI 回复
    answer = result["messages"][-1].content
    return {"answer": answer}

@app.get("/", summary="根路径")
async def root():
    return {"message": "天气查询助手 API 已启动，请访问 /docs 查看文档"}