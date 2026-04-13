"""
API 配置文件
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# ===================== 服务器配置 =====================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
SERVER_RELOAD = os.getenv("SERVER_RELOAD", "false").lower() == "true"

# ===================== 模型配置 =====================
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", str(BASE_DIR / "swin_bird_stage2_best.pth"))
CLASS_MAPPING_PATH = os.getenv("CLASS_MAPPING_PATH", str(BASE_DIR / "class_mapping.json"))
INFERENCE_DEVICE = os.getenv("INFERENCE_DEVICE", "auto")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.20))

# ===================== 文件上传配置 =====================
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

# ===================== 千问 Agent 配置 =====================
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_TIMEOUT = int(os.getenv("QWEN_TIMEOUT", 45))

# ===================== API配置 =====================
API_TITLE = "鸟类识别API"
API_DESCRIPTION = "支持上传鸟类图片进行自动识别、知识增强和历史记录管理"
API_VERSION = "3.0.0"

# ===================== 日志配置 =====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/api.log")

# ===================== 缓存配置 =====================
ENABLE_MODEL_CACHE = True
CACHE_MAX_PREDICTIONS = 1000

# ===================== 开发配置 =====================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*",
    ).split(",")
    if origin.strip()
]


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
        "agent": {
            "provider": "qwen",
            "base_url": QWEN_BASE_URL,
            "model": QWEN_MODEL,
            "enabled": bool(QWEN_API_KEY),
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
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(get_config(), indent=2, ensure_ascii=False))
