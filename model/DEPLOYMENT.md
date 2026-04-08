# 鸟类识别API - 部署与集成指南

## 📖 目录

1. [快速启动](#快速启动)
2. [API文档](#api文档)
3. [集成方式](#集成方式)
4. [生产部署](#生产部署)
5. [常见问题](#常见问题)

---

## 🚀 快速启动

### Windows用户

```bash
# 方式一：双击运行启动脚本（最简单）
run.bat

# 方式二：手动启动
# 1. 打开PowerShell或CMD
# 2. 进入项目目录
cd d:\xwechat_files\wxid_sbv0x7f95mny12_0917\msg\file\2026-04\model

# 3. 运行启动脚本
python api.py
# 或
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Linux/Mac用户

```bash
# 方式一：运行bash脚本
chmod +x run.sh
./run.sh

# 方式二：手动启动
python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 验证启动成功

访问以下任意链接验证:
- 🔗 http://localhost:8000 - API主页
- 📖 http://localhost:8000/docs - Swagger文档（推荐）
- 📖 http://localhost:8000/redoc - ReDoc文档

---

## 📚 API文档

### 完整文档详见

👉 [API_GUIDE.md](API_GUIDE.md) - 详细API使用说明

### 核心端点一览

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/predict` | POST | 上传图片进行识别 |
| `/api/predict/with_visualization` | POST | 上传图片识别+获取特征数据 |
| `/api/health` | GET | 检查服务状态 |
| `/api/info` | GET | 获取API信息和类别列表 |

---

## 🔌 集成方式

### 1. Python客户端集成

#### 选项A：使用项目提供的客户端

```python
from client import BirdIdentificationAPIClient

# 初始化客户端
client = BirdIdentificationAPIClient(base_url="http://localhost:8000")

# 执行识别
result = client.predict("bird_image.jpg")

if result.get('success'):
    for item in result['data']['top_3']:
        print(f"{item['rank']}. {item['species']} - {item['confidence']:.2%}")
else:
    print(f"错误: {result.get('error')}")
```

#### 选项B：直接使用requests

```python
import requests

url = "http://localhost:8000/api/predict"
with open("bird_image.jpg", "rb") as f:
    response = requests.post(url, files={"file": f})

result = response.json()
print(result)
```

### 2. JavaScript/Web前端集成

```javascript
// 使用Fetch API
async function identifyBird(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
        result.data.top_3.forEach(item => {
            console.log(`${item.rank}. ${item.species} - ${(item.confidence * 100).toFixed(2)}%`);
        });
    } else {
        console.error('识别失败:', result.error);
    }
}

// 使用示例
document.getElementById('imageInput').addEventListener('change', (e) => {
    identifyBird(e.target.files[0]);
});
```

### 3. cURL命令行集成

```bash
# 基础识别
curl -X POST "http://localhost:8000/api/predict" \
  -F "file=@bird_image.jpg" \
  -H "accept: application/json" | json_pp

# 带可视化数据
curl -X POST "http://localhost:8000/api/predict/with_visualization" \
  -F "file=@bird_image.jpg" | json_pp

# 检查服务状态
curl "http://localhost:8000/api/health" | json_pp
```

### 4. 其他语言集成

#### Node.js/Express

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function identifyBirdNode(imagePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));
    
    const response = await axios.post(
        'http://localhost:8000/api/predict',
        form,
        { headers: form.getHeaders() }
    );
    
    return response.data;
}
```

#### Java

```java
import okhttp3.*;
import java.io.File;

public class BirdIdentificationClient {
    private static final String API_URL = "http://localhost:8000/api/predict";
    
    public static void identifyBird(String imagePath) throws Exception {
        OkHttpClient client = new OkHttpClient();
        
        File file = new File(imagePath);
        RequestBody fileBody = RequestBody.create(
            MediaType.parse("image/jpeg"), file
        );
        
        RequestBody requestBody = new MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.getName(), fileBody)
            .build();
        
        Request request = new Request.Builder()
            .url(API_URL)
            .post(requestBody)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            System.out.println(response.body().string());
        }
    }
}
```

---

## 🏢 生产部署

### 部署清单

- [ ] 模型文件（swin_bird_stage2_best.pth）已复制
- [ ] 类别映射文件（class_mapping.json）已复制
- [ ] 依赖已安装（pip install -r requirements.txt）
- [ ] 配置文件已审查（config.py 或 .env）
- [ ] SSL证书已配置（如需HTTPS）
- [ ] 日志路径已创建（logs/）
- [ ] 性能测试已完成
- [ ] 备份策略已制定

### 选项1：使用Gunicorn + Uvicorn（Linux/Mac推荐）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动多worker进程（4个workers）
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  api:app
```

### 选项2：使用Docker（跨平台推荐）

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install -i https://pypi.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "api.py"]
```

**构建和运行：**

```bash
# 构建镜像
docker build -t bird-identification-api:1.0 .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --name bird-api \
  --gpus all \  # 如果需要GPU支持
  bird-identification-api:1.0

# 查看日志
docker logs -f bird-api

# 停止容器
docker stop bird-api
```

### 选项3：使用Nginx反向代理

```nginx
# /etc/nginx/sites-available/bird-api
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置（处理大图片上传）
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**启用配置：**

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/bird-api /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 选项4：使用Systemd服务（Linux）

```ini
# /etc/systemd/system/bird-api.service
[Unit]
Description=Bird Identification API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/bird-api
ExecStart=/opt/bird-api/venv/bin/python -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**管理服务：**

```bash
# 启动服务
sudo systemctl start bird-api

# 停止服务
sudo systemctl stop bird-api

# 重启服务
sudo systemctl restart bird-api

# 查看状态
sudo systemctl status bird-api

# 查看日志
sudo journalctl -u bird-api -f
```

### 性能优化建议

```python
# 在api.py中添加
from fastapi.middleware.gzip import GZIPMiddleware

# 启用Gzip压缩
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 添加速率限制（需安装 slowapi）
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## 🐛 常见问题

### Q1: 如何在后台运行API？

**Linux/Mac:**
```bash
nohup python -m uvicorn api:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
```

**Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "-m uvicorn api:app --host 0.0.0.0 --port 8000" -NoNewWindow
```

### Q2: 如何更改监听端口？

编辑 `run.bat` 或 `run.sh` 文件，或运行：
```bash
python -m uvicorn api:app --port 9000
```

### Q3: 如何启用CORS（跨域请求）？

在 `api.py` 中添加：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定具体的域名: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q4: 如何增加上传文件大小限制？

修改 `config.py`:
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 改为100MB
```

### Q5: GPU识别失败如何解决？

运行以下命令检查：
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

如果输出 `False`，说明未检测到GPU。请确保已安装CUDA和cudnn。

### Q6: 如何查看详细日志？

启动时添加日志参数：
```bash
python -m uvicorn api:app --log-level debug
```

---

## 📊 监控和维护

### 健康检查

定期检查API状态：
```bash
curl http://localhost:8000/api/health
```

### 性能监控

使用工具如 `locust` 进行负载测试：

```python
# locustfile.py
from locust import HttpUser, task

class APIUser(HttpUser):
    @task
    def predict_bird(self):
        with open("test_bird.jpg", "rb") as f:
            self.client.post("/api/predict", files={"file": f})
```

运行测试：
```bash
pip install locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## 📝 更新日志

### v1.0.0
- ✅ 初始发布
- ✅ 支持图片上传和识别
- ✅ 返回Top-3结果
- ✅ 自动API文档
- ✅ 健康检查端点

---

## 📞 技术支持

有问题？请检查：
1. [API_GUIDE.md](API_GUIDE.md) - API详细文档
2. [Readme.md](Readme.md) - 项目概览
3. http://localhost:8000/docs - 交互式API文档
