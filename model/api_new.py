"""
鸟类识别API接口 - 完整版本
支持：图片上传、模型推理、热力图可视化、历史记录、CORS跨域
"""

import torch
import json
import io
import base64
import uuid
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from torchvision import transforms
from contextlib import asynccontextmanager
import logging
import os

from model import SwinBirdModel
from perception_engine import BirdPerceptionEngine
from model_explain.explain_engine import ExplainEngine
from config import CORS_ENABLED, CORS_ORIGINS, CONFIDENCE_THRESHOLD

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===================== 历史记录存储 =====================
class HistoryStorage:
    """内存中的历史记录存储（可扩展为数据库）"""
    def __init__(self, max_records=100):
        self.records = []
        self.max_records = max_records
    
    def add_record(self, species: str, confidence: float, top_3: list, timestamp: datetime = None) -> str:
        """添加记录，返回记录ID"""
        record_id = str(uuid.uuid4())[:8]
        record = {
            "id": record_id,
            "species": species,
            "confidence": confidence,
            "top_3": top_3,
            "timestamp": (timestamp or datetime.now()).isoformat()
        }
        self.records.insert(0, record)  # 最新的记录放在最前
        
        # 保持最近的max_records条记录
        if len(self.records) > self.max_records:
            self.records = self.records[:self.max_records]
        return record_id
    
    def get_all_records(self) -> list:
        """获取所有记录"""
        return self.records
    
    def delete_record(self, record_id: str) -> bool:
        """删除指定记录"""
        for i, record in enumerate(self.records):
            if record["id"] == record_id:
                self.records.pop(i)
                return True
        return False


# ===================== 模型加载与管理 =====================
class ModelManager:
    """单例模式管理模型生命周期"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"使用设备: {self.device}")
            
            # 加载类别映射
            with open('class_mapping.json', 'r', encoding='utf-8') as f:
                class_map = json.load(f)
                self.class_names = [class_map[str(i)] for i in range(len(class_map))]
                logger.info(f"加载了 {len(self.class_names)} 个鸟类类别")
            
            # 加载模型
            weights_path = 'swin_bird_stage2_best.pth'
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"模型文件不存在: {weights_path}")
            
            self.model = SwinBirdModel(num_classes=len(self.class_names))
            checkpoint = torch.load(weights_path, map_location=self.device)
            state_dict = checkpoint['model_state_dict'] if 'model_state_dict' in checkpoint else checkpoint
            self.model.load_state_dict(state_dict)
            logger.info("模型加载成功")
            
            # 创建推理引擎
            self.engine = BirdPerceptionEngine(self.model, self.device, self.class_names)
            
            # 创建可解释性引擎
            self.explain_engine = ExplainEngine(self.model, self.device)
            
            # 图像预处理transforms
            self.transform = transforms.Compose([
                transforms.Resize((384, 384)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            # 创建历史记录存储
            self.history = HistoryStorage(max_records=100)
            
            self.initialized = True
    
    def infer(self, image_path):
        """执行推理"""
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0)
        result = self.engine.infer(image_tensor)
        return result, image


def generate_heatmap_base64(image_tensor, target_class_idx, model_manager) -> str:
    """生成Grad-CAM++热力图并返回Base64编码"""
    try:
        # 生成Grad-CAM++热力图
        gradcam_heatmap = model_manager.explain_engine.generate_heatmaps(
            image_tensor.to(model_manager.device),
            target_class_idx
        )
        
        # 获取原始图像（反归一化）
        original_image = image_tensor[0].cpu().numpy().transpose(1, 2, 0)
        original_image = np.clip(original_image * np.array([0.229, 0.224, 0.225]) + 
                                 np.array([0.485, 0.456, 0.406]), 0, 1)
        
        # 融合和可视化
        overlay, crop_imgs = model_manager.explain_engine.fuse_and_visualize(
            gradcam_heatmap,
            original_image,
            top_n=3,
            crop_size=(448, 448)
        )
        
        # 转换为BGR（OpenCV格式）并编码为PNG
        overlay_bgr = cv2.cvtColor((overlay * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        success, buffer = cv2.imencode('.png', overlay_bgr)
        
        if success:
            # 转换为Base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/png;base64,{base64_str}"
        else:
            logger.warning("热力图编码失败")
            return None
    except Exception as e:
        logger.error(f"热力图生成失败: {str(e)}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动，初始化模型...")
    try:
        ModelManager()
        logger.info("模型初始化成功")
    except Exception as e:
        logger.error(f"模型初始化失败: {str(e)}")
        raise
    yield
    logger.info("应用关闭")


# ===================== FastAPI应用初始化 =====================
app = FastAPI(
    title="鸟类识别API",
    description="支持上传鸟类图片进行自动识别、返回热力图可视化和历史记录",
    version="2.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
if CORS_ENABLED:
    origins = [origin.strip() for origin in CORS_ORIGINS]
    logger.info(f"启用CORS，允许的源: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.info("CORS已禁用")


# ===================== API 端点 =====================

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    """
    鸟类图片识别接口（基础版本）
    
    Args:
        file: 上传的图片文件 (jpg/jpeg/png/webp)
    
    Returns:
        {
            "success": true,
            "data": {
                "top_3": [
                    {
                        "rank": 1,
                        "species": "鸟类物种名",
                        "confidence": 0.75
                    },
                    ...
                ],
                "suggestion": "如果置信度低于阈值的警告提示"
            }
        }
    """
    try:
        # 验证文件类型
        allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持: JPEG, PNG, WebP。接收到: {file.content_type}"
            )
        
        # 读取上传的文件
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="上传文件为空")
        
        # 加载图片
        try:
            image = Image.open(io.BytesIO(contents)).convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无法解析图片文件: {str(e)}")
        
        # 获取模型管理器并执行推理
        manager = ModelManager()
        image_tensor = manager.transform(image).unsqueeze(0)
        inference_result = manager.engine.infer(image_tensor)
        
        # 组织返回结果
        top_3_with_rank = [
            {
                "rank": idx + 1,
                "species": item["species"],
                "confidence": round(item["confidence"], 4)
            }
            for idx, item in enumerate(inference_result["top_3"])
        ]
        
        # 添加到历史记录
        manager.history.add_record(
            species=inference_result["top_3"][0]["species"],
            confidence=inference_result["top_3"][0]["confidence"],
            top_3=top_3_with_rank
        )
        
        response = {
            "success": True,
            "data": {
                "top_3": top_3_with_rank,
                "suggestion": inference_result.get("suggestion"),
            }
        }
        
        logger.info(f"推理成功 - 最高置信度: {inference_result['top_3'][0]['confidence']:.2%}")
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推理失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"推理失败: {str(e)}"
            }
        )


@app.post("/api/predict/with_visualization")
async def predict_with_visualization(file: UploadFile = File(...)):
    """
    鸟类识别接口（带可视化热力图）
    
    Returns:
        {
            "success": true,
            "data": {
                "top_3": [...],
                "suggestion": null,
                "heatmap_base64": "data:image/png;base64,..." # 实际的热力图图片
            }
        }
    """
    try:
        # 验证文件类型
        allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持: JPEG, PNG, WebP。接收到: {file.content_type}"
            )
        
        # 读取上传的文件
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="上传文件为空")
        
        # 加载图片
        try:
            image = Image.open(io.BytesIO(contents)).convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无法解析图片文件: {str(e)}")
        
        # 获取模型管理器并执行推理
        manager = ModelManager()
        image_tensor = manager.transform(image).unsqueeze(0)
        inference_result = manager.engine.infer(image_tensor)
        
        # 组织返回结果
        top_3_with_rank = [
            {
                "rank": idx + 1,
                "species": item["species"],
                "confidence": round(item["confidence"], 4)
            }
            for idx, item in enumerate(inference_result["top_3"])
        ]
        
        # 生成热力图
        target_class_idx = manager.model.backbone.backbone.norm.weight.shape[0] - 1  # 最高置信度的类别
        with torch.no_grad():
            logits, _ = manager.model(image_tensor.to(manager.device))
            target_class_idx = torch.argmax(logits[0]).item()
        
        heatmap_base64 = generate_heatmap_base64(image_tensor, target_class_idx, manager)
        
        # 添加到历史记录
        manager.history.add_record(
            species=inference_result["top_3"][0]["species"],
            confidence=inference_result["top_3"][0]["confidence"],
            top_3=top_3_with_rank
        )
        
        response = {
            "success": True,
            "data": {
                "top_3": top_3_with_rank,
                "suggestion": inference_result.get("suggestion"),
                "heatmap_base64": heatmap_base64
            }
        }
        
        logger.info(f"推理成功（带可视化）- 最高置信度: {inference_result['top_3'][0]['confidence']:.2%}")
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推理失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"推理失败: {str(e)}"
            }
        )


@app.get("/api/history")
async def get_history(limit: int = 20):
    """
    获取识别历史记录
    
    Args:
        limit: 返回最近的N条记录（默认20）
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": "abc12345",
                    "species": "物种名",
                    "confidence": 0.85,
                    "top_3": [...],
                    "timestamp": "2026-04-09T12:34:56.789..."
                },
                ...
            ]
        }
    """
    try:
        manager = ModelManager()
        all_records = manager.history.get_all_records()
        limited_records = all_records[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": limited_records,
            "total": len(all_records)
        })
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.delete("/api/history/{record_id}")
async def delete_history_record(record_id: str = Path(..., description="要删除的记录ID")):
    """
    删除指定的历史记录
    
    Args:
        record_id: 记录ID
    
    Returns:
        {
            "success": true,
            "message": "记录已删除"
        }
    """
    try:
        manager = ModelManager()
        if manager.history.delete_record(record_id):
            return JSONResponse(content={
                "success": True,
                "message": f"记录 {record_id} 已删除"
            })
        else:
            raise HTTPException(
                status_code=404,
                detail=f"记录 {record_id} 不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除记录失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.delete("/api/history")
async def clear_history():
    """
    清空所有历史记录
    
    Returns:
        {
            "success": true,
            "message": "所有历史记录已清空"
        }
    """
    try:
        manager = ModelManager()
        manager.history.records = []
        
        return JSONResponse(content={
            "success": True,
            "message": "所有历史记录已清空"
        })
    except Exception as e:
        logger.error(f"清空历史记录失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    try:
        manager = ModelManager()
        return JSONResponse(content={
            "status": "healthy",
            "device": str(manager.device),
            "model_loaded": True,
            "num_classes": len(manager.class_names),
            "cors_enabled": CORS_ENABLED
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/api/info")
async def get_info():
    """获取API信息和支持的类别列表"""
    try:
        manager = ModelManager()
        return JSONResponse(content={
            "success": True,
            "data": {
                "api_version": "2.0.0",
                "total_classes": len(manager.class_names),
                "device": str(manager.device),
                "model": "Swin Transformer (swin_base_patch4_window12_384)",
                "features": [
                    "基础识别 (/api/predict)",
                    "热力图可视化 (/api/predict/with_visualization)",
                    "历史记录管理 (/api/history)",
                    "CORS支持"
                ],
                "classes_sample": manager.class_names[:10]
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/")
async def root():
    """根路径返回API信息"""
    return {
        "message": "欢迎使用鸟类识别API v2.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": [
            {"path": "/api/predict", "method": "POST", "description": "上传图片进行识别"},
            {"path": "/api/predict/with_visualization", "method": "POST", "description": "上传图片进行识别（包含热力图）"},
            {"path": "/api/history", "method": "GET", "description": "获取识别历史记录"},
            {"path": "/api/history/{id}", "method": "DELETE", "description": "删除指定历史记录"},
            {"path": "/api/history", "method": "DELETE", "description": "清空所有历史记录"},
            {"path": "/api/health", "method": "GET", "description": "健康检查"},
            {"path": "/api/info", "method": "GET", "description": "获取API信息"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    # 运行: python api.py
    # 或: uvicorn api:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
