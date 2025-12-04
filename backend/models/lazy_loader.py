# backend/models/lazy_loader.py
"""Load images from HuggingFace or S3 with LRU in-memory caching"""
import os
from functools import lru_cache
from PIL import Image
import io
from config import Config

print(" Initializing image loader with LRU cache (maxsize=100)...")

# Initialize S3 client if needed
s3_client = None
if Config.USE_S3:
    try:
        import boto3
        s3_client = boto3.client(
            's3',
            region_name=Config.AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        print(f" S3 client initialized for region: {Config.AWS_REGION}")
    except Exception as e:
        print(f" S3 initialization failed: {e}")
        s3_client = None


@lru_cache(maxsize=100)
def load_image(image_path: str) -> Image.Image:
    """
    Load image from HuggingFace or S3 with in-memory LRU caching.
    
    Uses whichever is enabled via config:
    - if USE_HUGGINGFACE=true in config, it downloads from HuggingFace
    - if USE_S3=true in config, it downloads from S3 bucket
    
    First call: Downloads from source
    Repeated calls: Returns from cache (instantly LRU Cache)
    """
    
    print(f" load_image called: {image_path}")
    
    if Config.USE_HUGGINGFACE:
        return _load_from_huggingface(image_path)
    elif Config.USE_S3:
        return _load_from_s3(image_path)
    else:
        raise RuntimeError("No image source configured (enable USE_HUGGINGFACE or USE_S3)")


def _load_from_huggingface(image_path: str) -> Image.Image:
    """Load from HuggingFace with LRU caching"""
    from huggingface_hub import hf_hub_download
    
    # .npy paths are "gallery/img/WOMEN/..."
    # Strip "gallery/" prefix
    clean_path = image_path
    if clean_path.startswith("gallery/"):
        clean_path = clean_path[8:]  # Now: "img/WOMEN/..."
    
    # Remove "img/" prefix to get relative path
    if clean_path.startswith("img/"):
        clean_path = clean_path[4:]  # Now: "WOMEN/Blouses_Shirts/..."
    
    # HuggingFace dataset path structure
    hf_file_path = f"In_Shop_Clothes_Retrieval/Anno/densepose/img/{clean_path}"
    
    try:
        print(f" Downloading from HuggingFace: {hf_file_path}")
        
        # hf_hub_download method automatically caches to ~/.cache/huggingface/hub/
        file_path = hf_hub_download(
            repo_id=Config.HF_DATASET_ID,
            filename=hf_file_path,
            repo_type="dataset",
            cache_dir=os.path.expanduser("~/.cache/huggingface/hub")
        )
        
        print(f" Downloaded/cached at: {file_path}")
        
        # Load image into memory
        img = Image.open(file_path).convert("RGB")
        print(f"  Image loaded to memory: {img.size}")
        
        return img
        
    except Exception as e:
        print(f"  Error loading from HuggingFace: {str(e)}")
        raise RuntimeError(f"Failed to load image from HuggingFace: {str(e)}")


def _load_from_s3(image_path: str) -> Image.Image:
    """Load from S3 bucket with LRU caching"""
    
    if not s3_client:
        raise RuntimeError("S3 client not initialized")
    
    # .npy paths are "gallery/img/WOMEN/..."
    # S3 key structure: img/WOMEN/Blouses_Shirts/id_00000001/02_1_front.jpg
    
    s3_key = image_path
    # Remove "gallery/" prefix if present
    if s3_key.startswith("gallery/"):
        s3_key = s3_key[8:]  # Now: "img/WOMEN/..."
    
    try:
        print(f"Downloading from S3: s3://{Config.S3_BUCKET}/{s3_key}")
        
        # Download from S3
        response = s3_client.get_object(Bucket=Config.S3_BUCKET, Key=s3_key)
        img_data = response['Body'].read()
        
        print(f"Downloaded from S3: {len(img_data)} bytes")
        
        # Load image into memory
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        print(f"Image loaded to memory: {img.size}")
        
        return img
        
    except Exception as e:
        print(f"Error loading from S3: {str(e)}")
        raise RuntimeError(f"Failed to load image from S3: {str(e)}")


def get_cache_info() -> dict:
    """Get LRU cache statistics"""
    cache_info = load_image.cache_info()
    return {
        "hits": cache_info.hits,
        "misses": cache_info.misses,
        "maxsize": cache_info.maxsize,
        "currsize": cache_info.currsize
    }


def clear_cache():
    """Clear the LRU cache (useful for memory cleanup)"""
    load_image.cache_clear()
    print("  LRU cache cleared")
