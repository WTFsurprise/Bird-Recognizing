#  鸟类识别平台 - Bird Discovery Platform

一个完整的深度学习驱动的鸟类自动识别与分类系统，包含现代化的Web前端、高性能的FastAPI后端，以及Docker容器化部署支持。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18+-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009485)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)


## 项目结构

```
bird-discovery-platform/
├── model/                          # 后端应用 (FastAPI)
│   ├── api.py                      # 主API接口 (改进版2.0)
│   ├── main.py                     # 独立推理脚本
│   ├── model.py                    # 模型定义
│   ├── perception_engine.py        # 推理引擎
│   ├── config.py                   # 配置管理 (CORS启用)
│   ├── class_mapping.json          # 313个物种映射
│   ├── swin_bird_stage*.pth        # 预训练权重 (2个)
│   ├── requirements.txt            # Python依赖
│   ├── Dockerfile                  # 后端容器配置
│   ├── DEPLOYMENT.md               # 部署指南
│   └── model_explain/              # 热力图分析模块
│
├── frontend/                       # 前端应用 (React)
│   ├── src/
│   │   ├── components/             # React组件
│   │   │   ├── UploadZone.jsx     # 上传区域
│   │   │   ├── ResultCard.jsx     # 结果展示
│   │   │   ├── HistoryPanel.jsx   # 历史记录
│   │   │   └── Alerts.jsx         # 提示组件
│   │   ├── context/                # 状态管理
│   │   │   └── AppContext.jsx     # 全局状态
│   │   ├── api/                    # API调用层
│   │   │   └── birdService.js     # API服务
│   │   ├── styles/
│   │   │   └── index.css          # 全局样式
│   │   ├── App.jsx                # 主应用组件
│   │   └── main.jsx               # 应用入口
│   ├── index.html                  # HTML入口
│   ├── vite.config.js              # Vite构建配置
│   ├── tailwind.config.js          # Tailwind配置
│   ├── nginx.conf                  # Nginx配置
│   ├── Dockerfile                  # 前端容器配置
│   ├── package.json                # Node依赖
│   ├── README.md                   # 前端说明
│   └── .gitignore
│
├── docker-compose.yml              # Docker编排配置
├── .gitignore
└── README.md                       # 本文件
```

## 快速开始

### 方式1: Docker Compose (推荐)

最简单的部署方式，一键启动前后端：

```bash
# 进入项目目录
cd bird-discovery-platform

# 启动所有服务
docker-compose up

# 或后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f
```

**访问应用：**
- 前端：http://localhost
- 后端 API：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs

### 方式2: 本地开发

#### 后端设置

```bash
cd model

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行API服务
python api.py
# 或使用uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 开发模式 (自动代理API到 http://localhost:8000)
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

## API文档

### 基础识别端点

```bash
POST /api/predict
```

上传图片进行识别

**请求：**
```
Content-Type: multipart/form-data
file: <image.jpg>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "top_3": [
      {
        "rank": 1,
        "species": "Aquila chrysaetos",
        "confidence": 0.85
      },
      ...
    ],
    "suggestion": null
  }
}
```

### 识别 + 热力图端点

```bash
POST /api/predict/with_visualization
```

返回识别结果和热力图（Base64）

**响应包含：**
```json
{
  "success": true,
  "data": {
    "top_3": [...],
    "suggestion": null,
    "heatmap_base64": "data:image/png;base64,..."
  }
}
```

### 历史记录API

```bash
GET /api/history?limit=20        # 获取历史
DELETE /api/history/{record_id}  # 删除单条
DELETE /api/history              # 清空所有
```

### 其他端点

```bash
GET  /api/health    # 健康检查
GET  /api/info      # API信息
```

详见 Swagger 文档：http://localhost:8000/docs

## ⚙️ 配置说明

### 后端配置 (`model/config.py`)

主要环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SERVER_HOST` | `0.0.0.0` | 服务器监听地址 |
| `SERVER_PORT` | `8000` | API端口 |
| `INFERENCE_DEVICE` | `auto` | 推理设备 (auto/cuda/cpu) |
| `CONFIDENCE_THRESHOLD` | `0.20` | 置信度阈值 (20%) |
| `CORS_ENABLED` | `true` | 启用CORS跨域 |
| `CORS_ORIGINS` | `*` | 允许的跨域源 |
| `DEBUG` | `false` | 调试模式 |

### 前端配置 (`frontend/.env`)

```
VITE_API_URL=http://localhost:8000
```

## 📊 模型性能

| 指标 | 数值 |
|------|------|
| 模型架构 | Swin Transformer B384 |
| 训练数据 | 15,650 张图片 |
| 目标类别 | 313 种鸟类 |
| 验证准确率 | 65.43% |
| 输入尺寸 | 384×384 RGB |
| 推理时间 | ~800ms (GPU), ~3s (CPU) |

## 开发指南

### 添加新功能

1. **后端添加新API端点：**
   编辑 `model/api.py`，参考现有端点结构

2. **前端添加新组件：**
   在 `frontend/src/components/` 创建新文件

3. **修改样式：**
   - 全局样式：`frontend/src/styles/index.css`
   - Tailwind配置：`frontend/tailwind.config.js`

### 部署到生产环境

详见 `model/DEPLOYMENT.md`

主要步骤：
1. 构建Docker镜像
2. 配置环境变量
3. 设置反向代理（Nginx）
4. 配置SSL证书（HTTPS）
5. 启动容器

## 性能优化

- 后端使用单例模式缓存模型，避免重复加载
- 前端使用虚拟列表优化历史记录显示
- Nginx 启用 Gzip 压缩和静态资源缓存
- Docker 多阶段构建优化镜像大小

## 安全建议

1. **CORS配置** - 生产环境指定具体域名
2. **API认证** - 可考虑添加JWT令牌认证
3. **速率限制** - 防止滥用（后续扩展）
4. **输入验证** - 所有输入都经过验证
5. **HTTPS** - 生产环境部署SSL证书


