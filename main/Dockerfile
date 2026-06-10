FROM python:3.10-slim

WORKDIR /app

# 定义构建参数（API密钥）
ARG DASHSCOPE_API_KEY
ARG AMAP_API_KEY

# 设置环境变量
ENV DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
ENV AMAP_API_KEY=${AMAP_API_KEY}

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码文件
COPY weather_agent.py .
COPY api.py .

# 暴露 Gradio 端口
EXPOSE 7860

# 启动 Gradio 网页服务
CMD ["python", "api.py"]