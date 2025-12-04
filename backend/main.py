# backend/main.py
"""
Image Search API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time

from config import Config
from models.embedding import EmbeddingModel
from models.faiss_index import FAISSIndex
from routes import search, health, thumbnails

# Initialize models (global instances)
embedding_model = EmbeddingModel()
faiss_index = FAISSIndex()

# Inject into modules
search.embedding_model = embedding_model
search.faiss_index = faiss_index
health.faiss_index = faiss_index
thumbnails.faiss_index = faiss_index


def create_app():
    """Create and configure FastAPI app"""
    
    start_time = time.time()
    
    # Validate configuration
    t0 = time.time()
    Config.validate()
    print(f" Config validation: {time.time() - t0:.2f}s")
    
    # Load models
    print("=" * 50)
    print("Initializing Image Search API...")
    print("=" * 50)
    
    t0 = time.time()
    embedding_model.load()
    print(f" Embedding model load: {time.time() - t0:.2f}s")
    
    t0 = time.time()
    faiss_index.load(embedding_model.emb_dim)
    print(f" FAISS index load: {time.time() - t0:.2f}s")
    
    # Create app
    app = FastAPI(
        title="Image Search API",
        description="Search for similar images using DINOv2 + FAISS",
        version="1.0.0",
    )
    
    # Add CORS middleware
    if Config.CORS_ENABLED:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=Config.CORS_ORIGINS,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(search.router)
    app.include_router(thumbnails.router)
    
    # Mount static files (must be last)
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
    if os.path.exists(public_dir):
        app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
    
    total_time = time.time() - start_time
    print("=" * 50)
    print(f" API initialized successfully ({total_time:.2f}s)")
    print("=" * 50)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.BACKEND_HOST,
        port=Config.BACKEND_PORT,
        log_level="info",
    )
