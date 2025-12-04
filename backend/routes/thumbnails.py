# backend/routes/thumbnails.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import os
from config import Config
from models.lazy_loader import load_image, get_cache_info

# Will be injected by main.py
faiss_index = None

router = APIRouter(prefix="/api", tags=["thumbnails"])

# Initialize S3 client if needed
s3_client = None
if Config.USE_S3:
    import boto3
    s3_client = boto3.client('s3')


@router.get("/thumb/{idx}")
def thumb(idx: int, max_side: int = None):
    """Get thumbnail for image with LRU cache info"""
    if max_side is None:
        max_side = Config.THUMBNAIL_MAX_SIZE
    
    if idx < 0 or idx >= faiss_index.ntotal:
        raise HTTPException(status_code=404, detail="Index out of range")
    
    path = faiss_index.get_path(idx)
    print(f"\n Thumbnail request: idx={idx}, path={path}")
    
    try:
        if Config.USE_S3:
            img = _load_from_s3(path)
        else:
            # Load from HuggingFace with LRU cache
            img = load_image(path)
            cache_info = get_cache_info()
            print(f" LRU Cache - Hits: {cache_info['hits']}, Misses: {cache_info['misses']}, Size: {cache_info['currsize']}/{cache_info['maxsize']}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"   Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to open image: {str(e)}")
    
    # Resize if needed
    img = _resize_image(img, max_side)
    
    # Convert to JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=Config.THUMBNAIL_QUALITY)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/jpeg")


def _load_from_s3(path: str) -> Image.Image:
    """Load image from S3"""
    if not s3_client:
        raise HTTPException(status_code=500, detail="S3 not configured")
    
    if not path.startswith("s3://"):
        path = f"gallery/img/{path}"
    
    if path.startswith("s3://"):
        parts = path[5:].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else path
    else:
        bucket = Config.S3_BUCKET
        key = path
    
    response = s3_client.get_object(Bucket=bucket, Key=key)
    img_data = response['Body'].read()
    return Image.open(io.BytesIO(img_data)).convert("RGB")


def _load_from_local(path: str) -> Image.Image:
    """Load image using lazy loader (HF on-demand or local)"""
    return load_image(path)


def _resize_image(img: Image.Image, max_side: int) -> Image.Image:
    """Resize image if needed"""
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return img
