# 🐦 Bird Discovery Platform

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

### 项目简介

**鸟类识别与知识平台** 是一个基于深度学习的现代化鸟类自动识别与知识增强系统。用户上传一张鸟类照片，系统将：

1. 🔍 **自动识别鸟类物种** - 使用Swin Transformer深度学习模型识别313种鸟类
2. 🌐 **生成知识卡片** - 调用Qwen AI API生成栖息地、外观、习性等详细信息
3. 📚 **历史记录管理** - 保存所有识别记录便于查阅

### 主要特性

- ✅ **高精度识别** - 313种鸟类分类，识别准确率高
- ✅ **AI知识增强** - 集成Qwen AI生成符合条件的生态知识
- ✅ **现代化UI** - React + Tailwind CSS构建的响应式界面
- ✅ **完整API** - FastAPI实现RESTful接口，Swagger文档自动生成
- ✅ **Docker容器化** - 一键部署，免环境配置
- ✅ **CORS支持** - 跨域请求配置，支持多源访问
- ✅ **运行时配置** - 灵活的环境变量配置系统

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

#### Q4: 热力图功能

**说明：** 热力图功能因库兼容性问题已禁用

**未来计划：** 后续版本将优化热力图实现，提供更稳定的模型注意力可视化

### 性能优化

| 优化点 | 方案 |
|-------|------|
| GPU计算 | 设置 `INFERENCE_DEVICE=cuda` |
| 并发请求 | 调整Uvicorn workers |
| 缓存 | 热力图通过base64编码内置 |
| 压缩 | 前端自动限制上传大小 |

### 许可证

MIT License

### 联系支持

- 🐛 报告Bug: [GitHub Issues](https://github.com/Phoinikas2002/Bird-Recognizing/issues)

---

## English Documentation

### Project Overview

**Bird Discovery Platform** is a modern AI-powered bird species recognition and knowledge enhancement system based on deep learning. Users upload a bird photo, and the system will:

1. 🔍 **Automatically Identify Bird Species** - Using Swin Transformer to recognize 313 bird species
2. 🌐 **Generate Knowledge Cards** - Call Qwen AI API to generate detailed information
3. 📚 **Manage Analysis History** - Save all recognition records

### Key Features

- ✅ **High-Accuracy Recognition** - 313 bird species classification
- ✅ **AI Knowledge Enhancement** - Integrated Qwen AI generates comprehensive information
- ✅ **Modern UI** - Responsive interface built with React + Tailwind CSS
- ✅ **Complete API** - RESTful API with FastAPI and Swagger docs
- ✅ **Docker Containerized** - One-click deployment
- ✅ **CORS Support** - Cross-origin request configuration
- ✅ **Runtime Configuration** - Flexible environment variables

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

#### Q4: Heatmap Feature

**Note:** Heatmap visualization feature disabled for stability

**Future:** Will be optimized in upcoming releases

### Performance Tuning

| Optimization | Solution |
|--------------|----------|
| GPU | Set `INFERENCE_DEVICE=cuda` |
| Concurrency | Adjust Uvicorn workers |
| Caching | Built-in via base64 |
| Compression | Frontend auto-limits |

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### License

MIT License
# 🐦 Bird Discovery Platform

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

### 项目简介

**鸟类识别与知识平台** 是一个基于深度学习的现代化鸟类自动识别与知识增强系统。用户上传一张鸟类照片，系统将：

1. 🔍 **自动识别鸟类物种** - 使用Swin Transformer深度学习模型识别313种鸟类
2. 🌐 **生成知识卡片** - 调用Qwen AI API生成栖息地、外观、习性等详细信息
3. 📊 **可视化热力图** - 展示模型注意力区域，解释识别依据
4. 📚 **历史记录管理** - 保存所有识别记录便于查阅

### 主要特性

- ✅ **高精度识别** - 313种鸟类分类，结合热力图可视化解释
- ✅ **AI知识增强** - 集成Qwen AI生成符合条件的生态知识
- ✅ **现代化UI** - React + Tailwind CSS构建的响应式界面
- ✅ **完整API** - FastAPI实现RESTful接口，Swagger文档自动生成
- ✅ **Docker容器化** - 一键部署，免环境配置
- ✅ **CORS支持** - 跨域请求配置，支持多源访问
- ✅ **运行时配置** - 灵活的环境变量配置系统

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
│   │   └── explain_engine.py          # GradCAM热力图生成
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
      "heatmap_base64": "data:image/png;base64,..."
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

#### 3. 识别 + 热力图

```http
POST /api/predict/with_visualization
Content-Type: multipart/form-data

file: <image_file>
```

#### 4. 健康检测

```http
GET /api/health
```

#### 5. 系统信息

```http
GET /api/info
```

#### 6. 历史记录

```http
GET /api/history?limit=50
```

#### 7. 清空历史

```http
DELETE /api/history
```

### 功能使用指南

#### 1. 上传识别

1. 打开 http://localhost
2. 在上传区域拖拽或点击选择鸟类图片
3. 系统自动开始分析
4. 查看识别结果、热力图和知识卡片

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

### 性能优化

| 优化点 | 方案 |
|-------|------|
| GPU计算 | 设置 `INFERENCE_DEVICE=cuda` |
| 并发请求 | 调整Uvicorn workers |
| 缓存 | 热力图通过base64编码内置 |
| 压缩 | 前端自动限制上传大小 |

### 许可证

MIT License

### 联系支持

- 🐛 报告Bug: [GitHub Issues](https://github.com/Phoinikas2002/Bird-Recognizing/issues)

---

## English Documentation

### Project Overview

**Bird Discovery Platform** is a modern AI-powered bird species recognition and knowledge enhancement system based on deep learning. Users upload a bird photo, and the system will:

1. 🔍 **Automatically Identify Bird Species** - Using Swin Transformer to recognize 313 bird species
2. 🌐 **Generate Knowledge Cards** - Call Qwen AI API to generate detailed information
3.  **Manage Analysis History** - Save all recognition records

### Key Features

- ✅ **High-Accuracy Recognition** - 313 bird species classification
- ✅ **AI Knowledge Enhancement** - Integrated Qwen AI generates comprehensive information
- ✅ **Modern UI** - Responsive interface built with React + Tailwind CSS
- ✅ **Complete API** - RESTful API with FastAPI and Swagger docs
- ✅ **Docker Containerized** - One-click deployment
- ✅ **CORS Support** - Cross-origin request configuration
- ✅ **Runtime Configuration** - Flexible environment variables

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

#### 3. Recognition + Heatmap

```http
POST /api/predict/with_visualization
Content-Type: multipart/form-data
file: <image_file>
```

#### 4. Health Check

```http
GET /api/health
```

#### 5. System Info

```http
GET /api/info
```

#### 6. Get History

```http
GET /api/history?limit=50
```

#### 7. Clear History

```http
DELETE /api/history
```

### Usage Guide

#### 1. Upload & Recognize

1. Open http://localhost
2. Drag and drop or click to select a bird image
3. System automatically analyzes
4. View results, heatmap, and knowledge card

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


### Performance Tuning

| Optimization | Solution |
|--------------|----------|
| GPU | Set `INFERENCE_DEVICE=cuda` |
| Concurrency | Adjust Uvicorn workers |
| Caching | Built-in via base64 |
| Compression | Frontend auto-limits |

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### License

MIT License

### Support

- 🐛 Report Issues: [GitHub Issues](https://github.com/Phoinikas2002/Bird-Recognizing/issues)

---

<div align="center">

Made with ❤️ by the Bird Discovery Team

[![GitHub stars](https://img.shields.io/github/stars/Phoinikas2002/Bird-Recognizing?style=social)](https://github.com/Phoinikas2002/Bird-Recognizing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>
# 🐦 Bird Discovery Platform

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

### 项目简介

**鸟类识别与知识平台** 是一个基于深度学习的现代化鸟类自动识别与知识增强系统。用户上传一张鸟类照片，系统将：

1. 🔍 **自动识别鸟类物种** - 使用Swin Transformer深度学习模型识别313种鸟类
2. 🌐 **生成知识卡片** - 调用Qwen AI API生成栖息地、外观、习性等详细信息
3. 📊 **可视化热力图** - 展示模型注意力区域，解释识别依据
4. 📚 **历史记录管理** - 保存所有识别记录便于查阅

### 主要特性

- ✅ **高精度识别** - 313种鸟类分类，结合热力图可视化解释
- ✅ **AI知识增强** - 集成Qwen AI生成符合条件的生态知识
- ✅ **现代化UI** - React + Tailwind CSS构建的响应式界面
- ✅ **完整API** - FastAPI实现RESTful接口，Swagger文档自动生成
- ✅ **Docker容器化** - 一键部署，免环境配置
- ✅ **CORS支持** - 跨域请求配置，支持多源访问
- ✅ **运行时配置** - 灵活的环境变量配置系统

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
├── model/                          # 后端应用 (FastAPI)
│   ├── api.py                      # 主API接口 (改进版2.0)
│   ├── main.py                     # 独立推理脚本
│   ├── model.py                    # 模型定义
│   ├── perception_engine.py        # 推理引擎
│   ├── config.py                   # 配置管理 (CORS启用)
│   ├── class_mapping.json          # 313个物种映射
│   ├── swin_bird_stage*.pth        # 预训练权重 (2个)
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
├── requirements.txt                # Python依赖（全项目统一）
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
pip install -r ../requirements.txt

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

### 一体化分析端点

```bash
POST /api/analyze
```

上传图片后返回模型识别结果、热力图和千问 Agent 生成的知识卡片。

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
    "analysis_id": "a1b2c3d4",
    "recognition": {
      "top_1": {
        "rank": 1,
        "species": "Aquila chrysaetos",
        "confidence": 0.85
      },
      "top_3": [...],
      "heatmap_base64": "data:image/png;base64,..."
    },
    "knowledge": {
      "summary": "...",
      "habitat": [...],
      "observation_tips": [...]
    }
  }
}
```

### 基础识别端点

```bash
POST /api/predict
```

仅返回模型识别结果，不包含知识增强内容。

### 识别 + 热力图端点

```bash
POST /api/predict/with_visualization
```

返回识别结果和热力图（Base64）。

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

## 配置说明

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
| `QWEN_API_KEY` | 空 | 千问兼容接口密钥 |
| `QWEN_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 千问兼容接口地址 |
| `QWEN_MODEL` | `qwen-plus` | 千问模型名称 |

如果没有提供模型权重文件，后端仍然可以启动，但会以“框架模式”运行；如果没有配置 `QWEN_API_KEY`，知识卡片会回退为本地模板内容。

### 前端配置 (`frontend/.env`)

```
VITE_API_URL=http://localhost:8000
```

## 模型性能

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


