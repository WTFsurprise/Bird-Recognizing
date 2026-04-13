#!/bin/bash
# 鸟类识别API启动脚本 (Linux/Mac)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_REQUIREMENTS="${SCRIPT_DIR}/../requirements.txt"

echo "=========================================="
echo "🚀 鸟类识别API启动脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查必要的文件
if [ ! -f "swin_bird_stage2_best.pth" ]; then
    echo "❌ 错误: 模型权重文件不存在 (swin_bird_stage2_best.pth)"
    exit 1
fi

if [ ! -f "class_mapping.json" ]; then
    echo "❌ 错误: 类别映射文件不存在 (class_mapping.json)"
    exit 1
fi

echo "✅ 模型文件检查通过"

# 安装依赖（如果需要）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "📦 激活虚拟环境..."
source venv/bin/activate

echo "📦 检查依赖..."
if ! pip show fastapi > /dev/null; then
    echo "📦 安装依赖..."
    if [ ! -f "${ROOT_REQUIREMENTS}" ]; then
        echo "❌ 错误: 未找到根目录 requirements.txt"
        exit 1
    fi
    pip install -q -r "${ROOT_REQUIREMENTS}"
fi

echo "✅ 依赖检查完成"

# 启动API
echo ""
echo "=========================================="
echo "🌐 启动API服务器..."
echo "=========================================="
echo ""
echo "📍 API地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo "📖 备用文档: http://localhost:8000/redoc"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
