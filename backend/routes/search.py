# backend/routes/search.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image
import io
import numpy as np

# These will be injected by main.py
embedding_model = None
faiss_index = None

router = APIRouter(prefix="/api", tags=["search"])


def build_results(D: np.ndarray, I: np.ndarray, k: int) -> list:
    """Build search results"""
    print(f"\n Building results for k={k}")
    print(f"D shape: {D.shape}, I shape: {I.shape}")
    print(f"Top indices: {I[0][:k]}")
    print(f"Top scores: {D[0][:k]}")
    
    results = []
    for rank, idx in enumerate(I[0][:k], start=1):
        idx = int(idx)
        label = faiss_index.get_label(idx)
        path = faiss_index.get_path(idx)
        score = float(D[0][rank - 1])
        
        print(f"   [{rank}] ID={idx}, Label={label}, Score={score:.4f}, Path={path}")
        
        results.append({
            "rank": rank,
            "id": idx,
            "label": label,
            "path": path,
            "thumb_url": f"/api/thumb/{idx}",
            "score": score,
        })
        
    print(f"Built {len(results)} results\n")
    return results


@router.post("/search-image")
async def search_image(file: UploadFile = File(...), k: int = Form(5)):
    """Search for similar images"""
    print(f"\n Search request: k={k}")
    
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        print(f"Reading file: {file.filename}")
        data = await file.read()
        print(f"File size: {len(data)} bytes")
        
        pil = Image.open(io.BytesIO(data)).convert("RGB")
        print(f"Image size: {pil.size}, mode: {pil.mode}")
    except Exception as e:
        print(f"Image read ERROR: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Encode image
    try:
        print(f"Encoding image...")
        q = embedding_model.encode(pil)
        print(f"Embedding shape: {q.shape}, dtype: {q.dtype}")
    except Exception as e:
        print(f"Encoding ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    
    # Search FAISS index
    try:
        print(f"Searching FAISS index...")
        D, I = faiss_index.search(q, k)
        print(f"Found distances: {D[0]}, indices: {I[0]}")
    except Exception as e:
        print(f"FAISS search ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    # Build results
    try:
        results = build_results(D, I, k)
    except Exception as e:
        print(f" Result building ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Result building failed: {str(e)}")
    
    return {"results": results}
