# backend/config.py
import os
from dotenv import load_dotenv

# Load config.env from parent directory
config_path = os.path.join(os.path.dirname(__file__), "..", "config.env")
load_dotenv(config_path)

print(f" Loading config from: {config_path}")

# Choose one hugging face or S3. It can also support locally uploaded search dataset, for that img folder should be in bundle/gallery/
USE_HUGGINGFACE = os.getenv("USE_HUGGINGFACE", "false").lower() == "true"
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"

print(f"USE_HUGGINGFACE: {USE_HUGGINGFACE}")
print(f"USE_S3: {USE_S3}")

if USE_HUGGINGFACE:
    # Images loaded on-demand by lazy_loader.py
    # No need to download entire dataset on startup
    BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bundle"))
    print(f" HuggingFace mode - images loaded on-demand")
elif USE_S3:
    # S3 bucket specified in config.env
    BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bundle"))
    print(f" S3 mode - images loaded from S3 bucket")
else:
    # Local bundle
    BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bundle"))
    print(f" Local bundle mode")

class Config:
    """Configuration"""
    USE_HUGGINGFACE = USE_HUGGINGFACE
    USE_S3 = USE_S3
    
    BUNDLE_DIR = BUNDLE_DIR
    MODEL_DIR = os.path.join(BUNDLE_DIR, "model")
    INDEX_DIR = os.path.join(BUNDLE_DIR, "index")
    
    # Model paths
    MODEL_ARCH_PATH = os.path.join(MODEL_DIR, "arch.json")
    MODEL_WEIGHTS_PATH = os.path.join(MODEL_DIR, "weights.pt")
    
    # Index paths
    FAISS_PATH = os.path.join(INDEX_DIR, "gallery.index")
    LABELS_PATH = os.path.join(INDEX_DIR, "gallery_labels.npy")
    PATHS_PATH = os.path.join(INDEX_DIR, "gallery_paths.npy")
    
    # API settings
    DEFAULT_K = int(os.getenv("DEFAULT_K", "5"))
    MAX_K = int(os.getenv("MAX_K", "100"))
    THUMBNAIL_MAX_SIZE = int(os.getenv("THUMBNAIL_MAX_SIZE", "320"))
    THUMBNAIL_QUALITY = int(os.getenv("THUMBNAIL_QUALITY", "85"))
    
    # Server settings
    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    
    # CORS settings
    CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Device
    DEVICE = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    
    # HuggingFace settings
    HF_DATASET_ID = os.getenv("HF_DATASET_ID", "neerachaudhary04/image-search-dataset")
    HF_DATASET_PATH = os.getenv("HF_DATASET_PATH", "In_Shop_Clothes_Retrieval/Anno/densepose")
    
    # AWS S3 settings
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    @staticmethod
    def validate():
        """Validate configuration - check required files exist"""
        required_files = [
            Config.MODEL_ARCH_PATH,
            Config.FAISS_PATH,
            Config.LABELS_PATH,
            Config.PATHS_PATH,
        ]
        
        for path in required_files:
            if not os.path.exists(path):
                raise RuntimeError(f"Required file not found: {path}")
