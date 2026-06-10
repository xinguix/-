# 🌤️ 天气查询智能助手

基于 **LangChain** + **通义千问** + **高德地图天气 API** 构建的智能天气查询助手。

## ✨ 功能特性

- 🌡️ **实时天气查询**：获取指定城市的实时天气信息（温度、湿度、风向风力等）
- 📅 **未来天气预报**：查询指定城市未来3-4天的天气预报
- 🌍 **全国城市支持**：支持国内主要城市的天气查询
- 🌐 **中英文双语**：支持中英文输入查询
- 💬 **对话记忆**：智能记住上下文，支持连续对话
- 🖥️ **Web 界面**：基于 Gradio 的友好聊天界面

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Docker（可选）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API 密钥

创建 `.env` 文件：

```env
# 通义千问 API 密钥（从阿里云获取）
DASHSCOPE_API_KEY=your_dashscope_api_key

# 高德地图 API 密钥（从高德地图开放平台获取）
AMAP_API_KEY=your_amap_api_key
```

### 运行方式

#### 方式 1：直接运行（终端模式）

```bash
python main/weather_agent.py
```

#### 方式 2：启动 Web 服务

```bash
python main/api.py
```

然后访问 http://localhost:7860 即可使用网页界面。

#### 方式 3：使用 Docker

```bash
# 构建镜像
docker build --build-arg DASHSCOPE_API_KEY=your_key --build-arg AMAP_API_KEY=your_key -t weather-agent .

# 运行容器
docker run -it --rm -p 7860:7860 weather-agent
```

## 📖 使用示例

### 实时天气查询

```
👤 你: 北京今天天气怎么样？
🤖 助手: 📍 北京北京市
         🌤️ 天气：晴
         🌡️ 温度：28℃
         💨 风向：东北风
         🍃 风力：3级
         💧 湿度：45%
```

### 天气预报查询

```
👤 你: 上海未来几天的天气预报
🤖 助手: 上海未来天气预报
         📆 2024-01-15 周一
            日间：晴，15℃
            夜间：多云，10℃
```

### 上下文对话

```
👤 你: 成都今天天气如何？
🤖 助手: 📍 四川成都...

👤 你: 这个城市明天天气怎么样？
🤖 助手: 成都未来天气预报...
```

## 🛠️ 技术栈

- **框架**: LangChain 0.2.x
- **大模型**: 通义千问 (qwen-plus)
- **天气数据**: 高德地图天气 API
- **Web 框架**: Gradio 4.x
- **容器化**: Docker

## 📁 项目结构

```
PythonProject7/
├── main/
│   ├── weather_agent.py    # 核心智能体逻辑
│   ├── api.py              # Web 界面入口
│   ├── requirements.txt     # 依赖列表
│   ├── Dockerfile          # Docker 配置
│   └── .dockerignore       # Docker 忽略文件
├── .env                    # 环境变量配置
└── .gitignore              # Git 忽略文件
```

## 🔧 API 密钥获取

1. **通义千问 API**：https://dashscope.aliyun.com/
2. **高德地图 API**：https://lbs.amap.com/

## 📝 注意事项

- 请妥善保管你的 API 密钥，不要泄露到公共仓库
- 使用 Docker 时，建议通过环境变量传递密钥，而不是硬编码
- 本项目仅供学习和个人使用

## 📄 许可证

MIT License