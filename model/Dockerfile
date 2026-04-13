# 后端 - 鸟类识别 FastAPI 应用
FROM python:3.10-slim

WORKDIR /app/model

# 安装系统依赖（OpenCV 和其他库）
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender1 libglib2.0-0 libgomp1 libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 复制根目录依赖文件
COPY requirements.txt /app/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制后端应用代码
COPY model/ /app/model/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "api.py"]
