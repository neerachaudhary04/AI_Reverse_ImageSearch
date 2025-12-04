# backend/routes/health.py
from fastapi import APIRouter
from config import Config

# Will be injected by main.py
faiss_index = None

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "ntotal": int(faiss_index.ntotal),
        "device": str(Config.DEVICE),
        "storage": "s3" if Config.USE_S3 else ("huggingface" if Config.USE_HUGGINGFACE else "local"),
    }
