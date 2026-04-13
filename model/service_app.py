from __future__ import annotations

import io
import json
import logging
import os
import re
import urllib.error
import urllib.request
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path as FilePath
from typing import Any, Dict, List, Optional, Tuple

import torch
from fastapi import FastAPI, File, HTTPException, Path as ApiPath, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from torchvision import transforms

from config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    ALLOWED_MIME_TYPES,
    CORS_ENABLED,
    CORS_ORIGINS,
    CLASS_MAPPING_PATH,
    CONFIDENCE_THRESHOLD,
    DEBUG,
    INFERENCE_DEVICE,
    MAX_FILE_SIZE,
    MODEL_WEIGHTS_PATH,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL,
    QWEN_TIMEOUT,
    SERVER_HOST,
    SERVER_PORT,
    SERVER_RELOAD,
)
from model import SwinBirdModel
from perception_engine import BirdPerceptionEngine

logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
logger = logging.getLogger(__name__)

BASE_DIR = FilePath(__file__).resolve().parent


def _resolve_device() -> torch.device:
    requested = (INFERENCE_DEVICE or "auto").lower()
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_class_names() -> List[str]:
    mapping_path = FilePath(CLASS_MAPPING_PATH)
    if not mapping_path.exists():
        logger.warning("类别映射文件不存在，使用兜底类别")
        return ["未知物种"]

    with mapping_path.open("r", encoding="utf-8") as file_handle:
        class_map = json.load(file_handle)

    if isinstance(class_map, dict):
        try:
            return [class_map[str(index)] for index in range(len(class_map))]
        except KeyError:
            ordered_items = sorted(class_map.items(), key=lambda item: int(item[0]))
            return [item[1] for item in ordered_items]

    if isinstance(class_map, list):
        return [str(item) for item in class_map]

    return ["未知物种"]


def _safe_float(value: Any, digits: int = 4) -> float:
    try:
        return round(float(value), digits)
    except Exception:
        return 0.0


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        snippet = cleaned[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return None
    return None


@dataclass
class HistoryRecord:
    id: str
    species: str
    confidence: float
    top_3: List[Dict[str, Any]]
    summary: str
    timestamp: str
    model_ready: bool
    agent_enabled: bool


class HistoryStorage:
    def __init__(self, max_records: int = 100):
        self.max_records = max_records
        self.records: List[Dict[str, Any]] = []

    def add_record(
        self,
        species: str,
        confidence: float,
        top_3: List[Dict[str, Any]],
        summary: str,
        model_ready: bool,
        agent_enabled: bool,
        timestamp: Optional[datetime] = None,
    ) -> str:
        record_id = str(uuid.uuid4())[:8]
        record = HistoryRecord(
            id=record_id,
            species=species,
            confidence=_safe_float(confidence, 4),
            top_3=top_3,
            summary=summary,
            timestamp=(timestamp or datetime.now()).isoformat(),
            model_ready=model_ready,
            agent_enabled=agent_enabled,
        )
        self.records.insert(0, record.__dict__)
        if len(self.records) > self.max_records:
            self.records = self.records[: self.max_records]
        return record_id

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.records

    def delete_record(self, record_id: str) -> bool:
        for index, record in enumerate(self.records):
            if record["id"] == record_id:
                self.records.pop(index)
                return True
        return False

    def clear(self) -> None:
        self.records = []


class KnowledgeAgent:
    def __init__(self) -> None:
        self.enabled = bool(QWEN_API_KEY)
        self.base_url = QWEN_BASE_URL.rstrip("/")
        self.model = QWEN_MODEL
        self.timeout = max(5, int(QWEN_TIMEOUT))

    def _fallback_payload(self, species: str, recognition: Dict[str, Any]) -> Dict[str, Any]:
        top_3 = recognition.get("top_3", [])
        top_names = [item.get("species", "Unknown Species") for item in top_3]
        confidence = recognition.get("top_1", {}).get("confidence", 0.0)
        suggestion = recognition.get("suggestion") or "When the image is clear, the model will provide more stable bird species judgments."
        return {
            "provider": "local-fallback",
            "model": "rule-based-template",
            "enabled": False,
            "species": species,
            "summary": f"Qwen API not configured. System has preserved the knowledge framework for {species}. It will be automatically expanded after QWEN_API_KEY is configured.",
            "basic_profile": {
                "classification_hint": "Local knowledge framework generated from model recognition results",
                "confidence_note": f"Current confidence is approximately {_safe_float(confidence * 100, 1)}%.",
                "recognition_hint": suggestion,
            },
            "habitat": ["Forest", "Wetland", "Grassland", "Mountain", "Urban Green Space"],
            "appearance": ["Body color, beak shape, wing and tail feathers are focuses", "Note head patterns and flight behavior"],
            "diet": ["Seeds", "Fruits", "Insects", "Small invertebrates"],
            "behavior": ["Activity time", "Social or solitary", "Vocalization"],
            "distribution": ["Distribution varies by species, may cover East Asia, Eurasia or globally"],
            "observation_tips": [
                "Try to capture side and front views",
                "Environmental background helps determine habitat",
                "Multiple shots recommended for distant subjects",
            ],
            "conservation": "Check local protection lists and conservation status.",
            "interesting_facts": [
                f"Top 3 candidates: {', '.join(top_names[:3]) if top_names else 'None'}",
                "More rich content available when Qwen Agent is enabled.",
            ],
            "search_terms": [species, "bird identification", "bird science", "birdwatching guide"],
        }

    def _build_prompt(self, species: str, recognition: Dict[str, Any]) -> str:
        top_lines = []
        for item in recognition.get("top_3", []):
            top_lines.append(f"- {item.get('species', 'Unknown Species')}: {_safe_float(item.get('confidence', 0.0) * 100, 1)}%")

        return (
            "You are a professional bird knowledge assistant who needs to organize encyclopedia-style content suitable for frontend display based on recognition results.\n"
            "Requirements:\n"
            "1. Output JSON only, no Markdown, no explanatory text.\n"
            "2. Keep the tone concise and fact-focused, suitable for direct rendering on web pages.\n"
            "3. If there is uncertainty in the recognition results, it should be clearly noted.\n"
            "4. Try to cover morphology, habitat, diet, behavior, distribution, observation tips and conservation information.\n"
            "5. Required return fields: species, summary, basic_profile, habitat, appearance, diet, behavior, distribution, observation_tips, conservation, interesting_facts, search_terms.\n\n"
            f"Recognized species: {species}\n"
            f"Recognition confidence: {_safe_float(recognition.get('top_1', {}).get('confidence', 0.0) * 100, 1)}%\n"
            "Top-3 candidates:\n"
            + "\n".join(top_lines)
        )

    def _call_qwen(self, species: str, recognition: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_prompt(species, recognition)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你只返回 JSON。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {QWEN_API_KEY}",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))

        content = response_payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _extract_json_block(content)
        if parsed is None:
            raise ValueError("千问响应无法解析为 JSON")
        parsed.setdefault("provider", "qwen")
        parsed.setdefault("model", self.model)
        parsed.setdefault("enabled", True)
        return parsed

    def enrich(self, species: str, recognition: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return self._fallback_payload(species, recognition)

        try:
            payload = self._call_qwen(species, recognition)
            if not isinstance(payload, dict):
                raise ValueError("千问响应格式异常")
            payload.setdefault("provider", "qwen")
            payload.setdefault("model", self.model)
            payload.setdefault("enabled", True)
            payload.setdefault("species", species)
            return payload
        except Exception as exc:
            logger.warning("Qwen Agent call failed, falling back to local knowledge framework: %s", exc)
            fallback = self._fallback_payload(species, recognition)
            fallback["agent_error"] = str(exc)
            return fallback


class ModelManager:
    _instance: Optional["ModelManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self.initialized:
            return

        self.device = _resolve_device()
        self.class_names = _load_class_names()
        self.model_ready = False
        self.model = None
        self.engine = None
        self.history = HistoryStorage(max_records=100)
        self.agent = KnowledgeAgent()
        self.transform = transforms.Compose(
            [
                transforms.Resize((384, 384)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        self._load_model()
        self.initialized = True

    def _load_model(self) -> None:
        weights_path = FilePath(MODEL_WEIGHTS_PATH)
        if not weights_path.exists():
            logger.warning("模型权重不存在，当前只启动框架和知识增强流程: %s", weights_path)
            return

        try:
            model = SwinBirdModel(num_classes=len(self.class_names))
            checkpoint = torch.load(weights_path, map_location=self.device)
            state_dict = checkpoint["model_state_dict"] if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint else checkpoint
            model.load_state_dict(state_dict)
            self.model = model.to(self.device)
            self.engine = BirdPerceptionEngine(self.model, self.device, self.class_names)
            self.model_ready = True

            logger.info("Model loaded successfully")
        except Exception as exc:
            logger.exception("Model loading failed, switching to demo mode: %s", exc)
            self.model_ready = False
            self.engine = None

    def _fallback_recognition(self, image_name: str = "") -> Dict[str, Any]:
        candidates = self.class_names[:3] if len(self.class_names) >= 3 else (self.class_names or ["Unknown Species"])
        base_confidences = [0.34, 0.22, 0.14]
        top_3 = []
        for index, species in enumerate(candidates):
            top_3.append(
                {
                    "rank": index + 1,
                    "species": species,
                    "confidence": base_confidences[index] if index < len(base_confidences) else 0.05,
                }
            )

        return {
            "top_3": top_3,
            "top_1": top_3[0],
            "suggestion": "Model weights not loaded, returning framework-level sample results. Please configure MODEL_WEIGHTS_PATH to enable real inference.",
            "model_ready": False,
            "image_name": image_name,
        }

    def predict(self, image: Image.Image, image_name: str = "") -> Dict[str, Any]:
        if not self.model_ready or self.engine is None:
            return self._fallback_recognition(image_name)

        image_tensor = self.transform(image).unsqueeze(0)
        inference_result = self.engine.infer(image_tensor, threshold=CONFIDENCE_THRESHOLD)
        top_3 = [
            {
                "rank": index + 1,
                "species": item["species"],
                "confidence": _safe_float(item["confidence"], 4),
            }
            for index, item in enumerate(inference_result["top_3"])
        ]
        top_1 = top_3[0]

        return {
            "top_3": top_3,
            "top_1": top_1,
            "suggestion": inference_result.get("suggestion"),
            "model_ready": True,
            "image_name": image_name,
        }

    def analyze_bytes(self, contents: bytes, image_name: str = "") -> Tuple[Dict[str, Any], Image.Image]:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        recognition = self.predict(image, image_name=image_name)
        top_species = recognition["top_1"]["species"]
        knowledge = self.agent.enrich(top_species, recognition)
        return {
            "recognition": recognition,
            "knowledge": knowledge,
        }, image


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动，初始化模型和知识增强模块")
    try:
        ModelManager()
        logger.info("服务初始化完成")
    except Exception as exc:
        logger.exception("服务初始化失败: %s", exc)
        raise
    yield
    logger.info("应用关闭")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

if CORS_ENABLED:
    origins = [origin for origin in CORS_ORIGINS if origin]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    manager = ModelManager()
    return {
        "message": "欢迎使用鸟类识别平台 API",
        "docs": "/docs",
        "health": "/api/health",
        "model_ready": manager.model_ready,
        "agent_ready": manager.agent.enabled,
        "endpoints": [
            {"path": "/api/analyze", "method": "POST", "description": "上传图片，返回识别结果 + 千问知识增强"},
            {"path": "/api/predict", "method": "POST", "description": "仅返回模型识别结果"},
            {"path": "/api/history", "method": "GET", "description": "获取历史记录"},
            {"path": "/api/health", "method": "GET", "description": "健康检查"},
            {"path": "/api/info", "method": "GET", "description": "API 和模型信息"},
        ],
    }


@app.get("/api/health")
async def health_check():
    manager = ModelManager()
    return JSONResponse(
        content={
            "status": "healthy",
            "device": str(manager.device),
            "model_loaded": manager.model_ready,
            "agent_ready": manager.agent.enabled,
            "num_classes": len(manager.class_names),
            "cors_enabled": CORS_ENABLED,
        }
    )


@app.get("/api/info")
async def get_info():
    manager = ModelManager()
    return JSONResponse(
        content={
            "success": True,
            "data": {
                "api_version": API_VERSION,
                "total_classes": len(manager.class_names),
                "device": str(manager.device),
                "model": "Swin Transformer (swin_base_patch4_window12_384)",
                "model_ready": manager.model_ready,
                "agent": {
                    "provider": "qwen",
                    "model": QWEN_MODEL,
                    "enabled": manager.agent.enabled,
                    "base_url": QWEN_BASE_URL,
                },
                "features": [
                    "图片上传识别",
                    "千问知识增强",
                    "历史记录管理",
                ],
                "classes_sample": manager.class_names[:10],
            },
        }
    )


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    return await _analyze_upload(file, include_agent=True)


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    return await _analyze_upload(file, include_agent=False)


async def _analyze_upload(file: UploadFile, include_agent: bool):
    try:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式。支持: JPEG, PNG, WebP。接收到: {file.content_type}")

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="上传文件为空")
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="文件过大，超过允许的上传上限")

        manager = ModelManager()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        recognition = manager.predict(image, image_name=file.filename or "")

        knowledge = manager.agent.enrich(recognition["top_1"]["species"], recognition) if include_agent else {}
        summary = knowledge.get("summary") or recognition.get("suggestion") or "鸟类识别已完成。"
        record_id = manager.history.add_record(
            species=recognition["top_1"]["species"],
            confidence=recognition["top_1"]["confidence"],
            top_3=recognition["top_3"],
            summary=summary,
            model_ready=recognition.get("model_ready", False),
            agent_enabled=knowledge.get("enabled", False),
        )

        payload = {
            "success": True,
            "data": {
                "analysis_id": record_id,
                "image": {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(contents),
                },
                "recognition": recognition,
                "knowledge": knowledge,
                "summary": summary,
            },
        }
        return JSONResponse(content=payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("分析失败: %s", exc)
        return JSONResponse(status_code=500, content={"success": False, "error": f"分析失败: {exc}"})


@app.get("/api/history")
async def get_history(limit: int = 20):
    manager = ModelManager()
    records = manager.history.get_all_records()[:limit]
    return JSONResponse(content={"success": True, "data": records, "total": len(manager.history.get_all_records())})


@app.delete("/api/history/{record_id}")
async def delete_history_record(record_id: str = ApiPath(..., description="要删除的记录ID")):
    manager = ModelManager()
    if manager.history.delete_record(record_id):
        return JSONResponse(content={"success": True, "message": f"记录 {record_id} 已删除"})
    raise HTTPException(status_code=404, detail=f"记录 {record_id} 不存在")


@app.delete("/api/history")
async def clear_history():
    manager = ModelManager()
    manager.history.clear()
    return JSONResponse(content={"success": True, "message": "所有历史记录已清空"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, reload=SERVER_RELOAD)
