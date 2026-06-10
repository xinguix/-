"""
天气查询智能体
基于 Langchain + 通义千问，使用高德地图天气API
"""

import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


#2.加载环境变量并检验
load_dotenv()
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  #通义千问的API KEY
AMAP_API_KEY = os.getenv("AMAP_API_KEY")   #高德地图的API KEY
if not DASHSCOPE_API_KEY:
    raise ValueError("请在 .env文件中配置 DASHSCOPE_API_KEY")
if not AMAP_API_KEY:
    raise ValueError("请在 .env文件中配置AMAP_API_KEY")



#初始化通义千问大模型
llm = ChatOpenAI(
    model="qwen-plus",
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
)


#4.定义工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称，例如'北京'，'上海','广州'")

@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """
    获取指定城市的实时天气信息
    根据城市名称查询当前天气状况、温度、湿度、风向风力等数据
    """
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
    "key": AMAP_API_KEY,
    "city": city,
    "extensions": "base",
    }

    try:
        response = requests.get(base_url,params=params, timeout=10)
        data = response.json()
        if data.get("status") !="1" or data.get("infocode")!="10000":
            return f"城市'{city}' 查询失败，请检查城市名称是否正确。"
        lives = data.get("lives",[])
        if not lives:
            return f"未找到城市'{city}'的天气信息。"
        weather_info = lives[0]
        province = weather_info.get("province","")
        city_name = weather_info.get("city",city)
        weather = weather_info.get("weather","")
        temperature = weather_info.get("temperature","")
        winddirection = weather_info.get("winddirection","")
        windpower = weather_info.get("windpower", "")
        humidity = weather_info.get("humidity","")

        result = (
            f"📍 {province}{city_name}\n"
            f"🌤️ 天气：{weather}\n"
            f"🌡️ 温度：{temperature}℃\n"
            f"💨 风向：{winddirection}\n"
            f"🍃 风力：{windpower}级\n"
            f"💧 湿度：{humidity}%"
        )
        # 处理编码问题
        result = result.encode('utf-8', 'replace').decode('utf-8')
        return result
    except requests.RequestException as e:
        return f"天气服务连接失败: {str(e)}"
    except Exception as e:
        return f"查询天气时出错: {str(e)}"



#5.定义工具2：多日天气预报（进阶功能）
class ForecastInput(BaseModel):
    """多日天气预报的参数结构"""
    city: str = Field(description="城市名称，例如'北京'，'上海'，'广州'")


@tool(args_schema=ForecastInput)
def get_weather_forecast(city: str) -> str:
    """
    获取制定城市未来3-4天的天气预报。
    包含了每日的天气状况、最高/最低温度、风力风向等
    """
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": AMAP_API_KEY,
        "city": city,
        "extensions": "all",
    }

    try:
        response = requests.get(base_url,params=params, timeout=10)
        data = response.json()

        if data.get("status")!="1" or data.get("infocode") != "10000":
            return f"城市'{city}'查询失败。"
        forecasts = data.get("forecasts",[])
        if not forecasts:
            return f"未找到城市'{city}' 的预报信息。"
        forecast_data = forecasts[0]
        city_name = forecast_data.get("city",city)
        casts = forecast_data.get("casts",[])
        if not casts:
            return f"未找到城市'{city_name}'的天气预报"
        result_lines = [f"{city_name}未来天气预报"]
        for cast in casts[:4]:
            date = cast.get("date","")
            day_weather = cast.get("dayweather","")
            night_weather = cast.get("nightweather","")
            day_temp = cast.get("daytemp","")
            night_temp = cast.get("nighttemp","")
            week = cast.get("week","")

            line = (
                f"\n📆 {date} 周{week}\n"
                f"   日间：{day_weather}，{day_temp}℃\n"
                f"   夜间：{night_weather}，{night_temp}℃"
            )
            result_lines.append(line)

        result = "\n".join(result_lines)
        # 处理编码问题
        result = result.encode('utf-8', 'replace').decode('utf-8')
        return result
    except requests.RequestException as e:
        return f"天气服务连接失败：{str(e)}"
    except Exception as e:
        return f"查询预报时出错：{str(e)}"


#6.创建智能体
tools = [get_weather, get_weather_forecast]
system_prompt = """
你是一个专业友好的天气助手，可以根据用户需求提供准确的天气信息。

你可以使用以下工具:
1. get_weather: 查询指定城市的实时天气（包括当前温度、天气状况、湿度、风向风力等）
2. get_weather_forecast: 查询指定城市的未来3-4天天气预报

理解用户意图的指南：

【实时天气查询的常见表达方式】
- 中文：今天天气怎么样？、现在天气如何？、当前温度多少？、今天冷不冷？、外面下雨吗？、空气质量怎么样？
- 英文：What's the weather today?、Current weather、Today's temperature、Is it raining?、How's the weather?

【天气预报查询的常见表达方式】
- 中文：未来几天天气、天气预报、这周天气怎么样？、明天天气、后天天气、周末天气
- 英文：Weather forecast、Forecast for next few days、Tomorrow's weather

【城市名称的识别】
- 城市名称通常出现在句子的开头或结尾，如"北京今天天气"或"今天天气北京"
- 也可能出现在句子中间，如"我想知道上海现在的天气"
- 支持国内主要城市：北京、上海、广州、深圳、杭州、成都、武汉、西安、南京等

使用规则：
1. 分析用户问题，识别是否包含城市名称
2. 如果用户没有明确说明城市，请主动询问用户所在城市
3. 根据用户意图选择合适的工具：
   - 询问当前状况（今天、现在、当前）→ 使用 get_weather
   - 询问未来情况（预报、明天、未来、下周）→ 使用 get_weather_forecast
4. 收到天气数据后，用简洁清晰的语言总结给用户，可以适当添加使用建议（如是否需要带伞、增减衣物等）
5. 回复语言应与用户提问语言保持一致（中文提问用中文回复，英文提问用英文回复）
"""

# 创建工具调用的 prompt，包含聊天历史支持
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("user", "{input}"),
    ("assistant", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
)



def main():
    """启动天气查询智能体，在终端进行交互式对话"""
    print("=" * 50)
    print("🤖 天气查询智能体已启动")
    print("=" * 50)
    print("支持查询：实时天气 / 未来天气预报")
    print("输入 'exit' 或 'quit' 退出\n")

    while True:
        user_input = input("👤 你: ").strip()
        # 退出条件
        if user_input.lower() in ["exit", "quit"]:
            print("👋 再见！")
            break
        if not user_input:
            continue

        try:
            # 调用 Agent 处理用户输入
            # agent.invoke 接收一个包含 messages 的字典，消息格式为 LangChain 标准格式
            result = agent_executor.invoke({
                "input": user_input
            })
            # 从返回结果中提取 AI 的回复内容
            answer = result["output"]
            # 处理编码问题
            answer = answer.encode('utf-8', 'replace').decode('utf-8')
            print(f"🤖 助手:\n{answer}\n")
        except Exception as e:
            print(f"❌ 出错了: {e}\n")


# ============================================================
# 脚本入口
# ============================================================
if __name__ == "__main__":
    main()