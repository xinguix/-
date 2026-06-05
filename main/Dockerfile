FROM python:3.10-slim

WORKDIR /app

# 不需要安装 gcc，依赖都是预编译包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 只复制必要的代码文件，不复制 .env
COPY weather_agent.py .
COPY api.py .

EXPOSE 7860

CMD ["python", "weather_agent.py"]