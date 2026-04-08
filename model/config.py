"""
API配置文件
"""

import os
from pathlib import Path

# ===================== 服务器配置 =====================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
SERVER_RELOAD = os.getenv("SERVER_RELOAD", "false").lower() == "true"

# ===================== 模型配置 =====================
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", "swin_bird_stage2_best.pth")
CLASS_MAPPING_PATH = os.getenv("CLASS_MAPPING_PATH", "class_mapping.json")

# 验证模型文件是否存在
if not Path(MODEL_WEIGHTS_PATH).exists():
    raise FileNotFoundError(f"模型权重文件不存在: {MODEL_WEIGHTS_PATH}")

if not Path(CLASS_MAPPING_PATH).exists():
    raise FileNotFoundError(f"类别映射文件不存在: {CLASS_MAPPING_PATH}")

# ===================== 推理配置 =====================
INFERENCE_DEVICE = os.getenv("INFERENCE_DEVICE", "auto")  # auto, cuda, cpu
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.20))  # 20%

# ===================== 文件上传配置 =====================
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

# ===================== API配置 =====================
API_TITLE = "鸟类识别API"
API_DESCRIPTION = "支持上传鸟类图片进行自动识别和分类，返回Top-3预测结果"
API_VERSION = "1.0.0"

# ===================== 日志配置 =====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/api.log")

# ===================== 缓存配置 =====================
ENABLE_MODEL_CACHE = True  # 是否启用模型单例缓存
CACHE_MAX_PREDICTIONS = 1000  # 最多缓存最近1000个预测结果（可选）

# ===================== 开发配置 =====================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"  # 默认启用CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*").split(",")

# ===================== 辅助函数 =====================
def get_config():
    """获取当前配置为字典"""
    return {
        "server": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "reload": SERVER_RELOAD,
        },
        "model": {
            "weights_path": MODEL_WEIGHTS_PATH,
            "class_mapping_path": CLASS_MAPPING_PATH,
            "device": INFERENCE_DEVICE,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        },
        "upload": {
            "max_file_size": MAX_FILE_SIZE,
            "allowed_extensions": list(ALLOWED_IMAGE_EXTENSIONS),
            "allowed_mime_types": list(ALLOWED_MIME_TYPES),
        },
        "api": {
            "title": API_TITLE,
            "description": API_DESCRIPTION,
            "version": API_VERSION,
        },
        "logging": {
            "level": LOG_LEVEL,
            "file": LOG_FILE,
        },
        "development": {
            "debug": DEBUG,
            "cors_enabled": CORS_ENABLED,
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_config(), indent=2, ensure_ascii=False))
