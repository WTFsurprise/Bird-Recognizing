#  Bird Discovery Platform

[中文](#中文) | [English](#english)

---

## 中文

### 项目简介

**鸟类识别与知识平台** 是一个基于深度学习的现代化鸟类自动识别与知识增强系统。用户上传一张鸟类照片，系统将：

1.  **自动识别鸟类物种** - 使用Swin Transformer深度学习模型识别313种鸟类
2.  **生成知识卡片** - 调用Qwen AI API生成栖息地、外观、习性等详细信息
3.  **历史记录管理** - 保存所有识别记录便于查阅

### 主要特性

-  **高精度识别** - 313种鸟类分类，识别准确率高
-  **AI知识增强** - 集成Qwen AI生成符合条件的生态知识
-  **现代化UI** - React + Tailwind CSS构建的响应式界面
-  **完整API** - FastAPI实现RESTful接口，Swagger文档自动生成
-  **Docker容器化** - 一键部署，免环境配置
-  **CORS支持** - 跨域请求配置，支持多源访问
-  **运行时配置** - 灵活的环境变量配置系统

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 | UI框架 |
| | Vite | 构建工具 |
| | Tailwind CSS | 样式框架 |
| | Axios | HTTP请求 |
| **后端** | FastAPI | Web框架 |
| | PyTorch | 深度学习框架 |
| | Swin Transformer | 鸟类识别模型 |
| **AI增强** | Qwen API | 知识生成 |
| **容器** | Docker | 容器化 |
| | Docker Compose | 编排 |
| | Nginx | 反向代理 |

### 项目结构

```
bird-discovery-platform/
│
├── model/                              # 后端应用核心
│   ├── service_app.py                  # FastAPI应用主文件
│   ├── config.py                       # 统一配置管理
│   ├── model.py                        # Swin模型定义
│   ├── perception_engine.py            # 推理引擎
│   ├── model_explain/
│   │   └── explain_engine.py          # GradCAM热力图生成（已禁用）
│   ├── Dockerfile                      # 后端镜像
│   ├── requirements.txt                # Python依赖
│   └── class_mapping.json              # 313种鸟类映射
│
├── frontend/                           # React前端应用
│   ├── src/
│   │   ├── App.jsx                    # 主应用组件
│   │   ├── main.jsx                   # 应用入口
│   │   ├── components/
│   │   │   ├── UploadZone.jsx        # 拖拽上传区
│   │   │   ├── ResultCard.jsx        # 结果展示卡片
│   │   │   ├── HistoryPanel.jsx      # 历史记录面板
│   │   │   └── Alerts.jsx            # 错误/加载提示
│   │   ├── context/
│   │   │   └── AppContext.jsx        # 全局状态管理
│   │   ├── api/
│   │   │   └── birdService.js        # API调用服务
│   │   └── styles/
│   │       └── index.css             # Tailwind样式
│   ├── index.html                     # HTML入口
│   ├── vite.config.js                 # Vite配置
│   ├── tailwind.config.js             # Tailwind配置
│   ├── nginx.conf                     # Nginx配置
│   ├── Dockerfile                     # 前端镜像
│   └── package.json                   # Node依赖
│
├── docker-compose.yml                 # Docker编排
├── requirements.txt                   # Python统一依赖
└── README.md                          # 本文档
```

### 快速开始

#### 方案1：Docker Compose（推荐）

**前置条件：**
- Docker 20.10+
- Docker Compose 2.0+

**启动步骤：**

```bash
# 1. 拉取项目
git clone https://github.com/Phoinikas2002/Bird-Recognizing.git
cd Bird-Recognizing

# 2. (可选) 配置Qwen API Key
export QWEN_API_KEY=sk-your-api-key-here

# 3. 启动所有服务
docker-compose up -d

# 4. 等待服务启动（约30秒）
# 查看日志确认后端就绪
docker-compose logs -f backend

# 5. 访问应用
# 前端: http://localhost
# 后端API: http://localhost:8000
# Swagger文档: http://localhost:8000/docs
```

#### 方案2：本地开发环境

**前置条件：**
- Python 3.10+
- Node.js 18+

**后端启动：**

```bash
# 1. 进入后端目录
cd model

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r ../requirements.txt

# 4. 设置环境变量
export QWEN_API_KEY=sk-your-api-key-here
export INFERENCE_DEVICE=auto  # 或 cuda/cpu

# 5. 启动API服务
uvicorn service_app:app --reload --host 0.0.0.0 --port 8000
```

**前端启动：**

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 访问 http://localhost:5173
```

### 环境配置

#### 后端环境变量 `.env` (可选)

```env
# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# 模型配置
MODEL_WEIGHTS_PATH=model/weights/swin_bird_base.pt
CLASS_MAPPING_PATH=model/class_mapping.json
CONFIDENCE_THRESHOLD=0.20
INFERENCE_DEVICE=auto

# API文件限制
MAX_FILE_SIZE=52428800  # 50MB

# CORS配置
CORS_ENABLED=true
CORS_ORIGINS=http://localhost,http://localhost:5173,http://frontend

# Qwen API配置（必需）
QWEN_API_KEY=sk-your-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
QWEN_TIMEOUT=30
```

#### 获取Qwen API Key

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册账号并实名认证
3. 创建API Key
4. 复制Key并配置到环境变量

### API 文档

#### 1. 图片分析 (完整功能)

```http
POST /api/analyze
Content-Type: multipart/form-data

file: <image_file>
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "analysis_id": "rec_20240414_001",
    "recognition": {
      "top_1": {
        "species": "Common Sparrow",
        "confidence": 0.92
      },
      "top_3": [
        {"rank": 1, "species": "Common Sparrow", "confidence": 0.92},
        {"rank": 2, "species": "Tree Sparrow", "confidence": 0.06},
        {"rank": 3, "species": "House Sparrow", "confidence": 0.02}
      ],
      "heatmap_base64": null
    },
    "knowledge": {
      "enabled": true,
      "model": "qwen-plus",
      "summary": "The common sparrow is a small passerine bird...",
      "habitat": ["Urban areas", "Gardens", "Farmland"],
      "appearance": ["Brown and grey plumage", "Small size"],
      "diet": ["Seeds", "Insects", "Grains"]
    }
  }
}
```

#### 2. 仅识别 (不包含知识)

```http
POST /api/predict
Content-Type: multipart/form-data

file: <image_file>
```

#### 3. 健康检测

```http
GET /api/health
```

#### 4. 系统信息

```http
GET /api/info
```

#### 5. 历史记录

```http
GET /api/history?limit=50
```

#### 6. 清空历史

```http
DELETE /api/history
```

### 功能使用指南

#### 1. 上传识别

1. 打开 http://localhost
2. 在上传区域拖拽或点击选择鸟类图片
3. 系统自动开始分析
4. 查看识别结果和知识卡片

#### 2. 查看历史

- 点击右侧的"Recent Analyses"查看历史记录
- 点击"Delete"删除单条记录
- 点击"Clear History"清空所有记录

#### 3. 检查系统状态

检查页面顶部的状态卡片：
- **Backend Status** - API服务是否在线
- **Bird CV Model** - 模型是否就绪
- **Qwen Agent** - 知识生成是否启用

### 常见问题

#### Q1: Qwen Agent显示"Fallback"

**原因：** QWEN_API_KEY未配置

**解决：**
```bash
export QWEN_API_KEY=sk-your-key-here
docker-compose down
docker-compose up -d
```

#### Q2: 后端容器启动失败

**检查日志：**
```bash
docker-compose logs backend
```

**常见原因：**
- GPU不可用但设置为CUDA → 改为 `INFERENCE_DEVICE=cpu`
- 内存不足 → 增加Docker内存限制
- 端口被占用 → 修改docker-compose.yml中的ports

#### Q3: 前端无法连接到后端

**检查：**
```bash
curl -I http://localhost:8000/api/health
```

### 联系支持

- 🐛 报告Bug: [GitHub Issues](https://github.com/Phoinikas2002/Bird-Recognizing/issues)

---

## English

### Project Overview

**Bird Discovery Platform** is a modern AI-powered bird species recognition and knowledge enhancement system based on deep learning. Users upload a bird photo, and the system will:

1.  **Automatically Identify Bird Species** - Using Swin Transformer to recognize 313 bird species
2.  **Generate Knowledge Cards** - Call Qwen AI API to generate detailed information
3.  **Manage Analysis History** - Save all recognition records

### Key Features

-  **High-Accuracy Recognition** - 313 bird species classification
-  **AI Knowledge Enhancement** - Integrated Qwen AI generates comprehensive information
-  **Modern UI** - Responsive interface built with React + Tailwind CSS
-  **Complete API** - RESTful API with FastAPI and Swagger docs
-  **Docker Containerized** - One-click deployment
-  **CORS Support** - Cross-origin request configuration
-  **Runtime Configuration** - Flexible environment variables

### Technology Stack

| Layer | Technology | Description |
|-------|-----------|-------------|
| **Frontend** | React 18 | UI Framework |
| | Vite | Build Tool |
| | Tailwind CSS | Style Framework |
| **Backend** | FastAPI | Web Framework |
| | PyTorch | Deep Learning |
| | Swin Transformer | Bird Model |
| **AI** | Qwen API | Knowledge Generation |
| **Container** | Docker | Platform |

### Quick Start

#### Option 1: Docker Compose (Recommended)

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Steps:**

```bash
# 1. Clone the repository
git clone https://github.com/Phoinikas2002/Bird-Recognizing.git
cd Bird-Recognizing

# 2. (Optional) Configure Qwen API Key
export QWEN_API_KEY=sk-your-api-key-here

# 3. Start all services
docker-compose up -d

# 4. Wait for services (~30 seconds)
# Check backend logs
docker-compose logs -f backend

# 5. Access the application
# Frontend: http://localhost
# Backend: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

#### Option 2: Local Development

**Prerequisites:**
- Python 3.10+
- Node.js 18+

**Backend:**

```bash
cd model
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
export QWEN_API_KEY=sk-your-api-key-here
uvicorn service_app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

### Environment Variables

#### Backend Configuration

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
LOG_LEVEL=INFO
INFERENCE_DEVICE=auto
CONFIDENCE_THRESHOLD=0.20
QWEN_API_KEY=sk-your-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
CORS_ENABLED=true
CORS_ORIGINS=http://localhost,http://localhost:5173
```

### API Documentation

#### 1. Complete Analysis

```http
POST /api/analyze
Content-Type: multipart/form-data
file: <image_file>
```

#### 2. Recognition Only

```http
POST /api/predict
Content-Type: multipart/form-data
file: <image_file>
```

#### 3. Health Check

```http
GET /api/health
```

#### 4. System Info

```http
GET /api/info
```

#### 5. Get History

```http
GET /api/history?limit=50
```

#### 6. Clear History

```http
DELETE /api/history
```

### Usage Guide

#### 1. Upload & Recognize

1. Open http://localhost
2. Drag and drop or click to select a bird image
3. System automatically analyzes
4. View results and knowledge card

#### 2. View History

- Click "Recent Analyses" to view history
- Click "Delete" to remove a record
- Click "Clear History" to remove all

#### 3. Check Status

Check status cards at the top:
- **Backend Status** - Is API online?
- **Bird CV Model** - Is model ready?
- **Qwen Agent** - Is knowledge enabled?

### FAQ

#### Q1: Qwen Agent Shows "Fallback"

**Cause:** QWEN_API_KEY not configured

**Solution:**
```bash
export QWEN_API_KEY=sk-your-key-here
docker-compose down
docker-compose up -d
```

#### Q2: Backend Container Fails

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- GPU unavailable → set `INFERENCE_DEVICE=cpu`
- Insufficient memory → increase Docker memory
- Port occupied → change ports in docker-compose.yml

#### Q3: Frontend Cannot Connect

**Check:**
```bash
curl -I http://localhost:8000/api/health
```

### Support

-  Report Issues: [GitHub Issues](https://github.com/Phoinikas2002/Bird-Recognizing/issues)

---


