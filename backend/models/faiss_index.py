# backend/models/faiss_index.py
import numpy as np
import faiss
from config import Config


class FAISSIndex:
    """Wrapper for FAISS index and metadata"""
    
    def __init__(self):
        self.index = None
        self.labels = None
        self.paths = None
        self.ntotal = 0
    
    def load(self, emb_dim: int):
        """Load FAISS index and metadata"""
        print(f"Loading FAISS index from {Config.FAISS_PATH}...")
        
        try:
            self.index = faiss.read_index(Config.FAISS_PATH)
            
            print(f"Index dim: {self.index.d}, emb_dim: {emb_dim}")
            if self.index.d != emb_dim:
                raise ValueError(f"Dimension mismatch! Index is {self.index.d}-dim but model outputs {emb_dim}-dim")
            
            # Load metadata
            self.labels = np.load(Config.LABELS_PATH, allow_pickle=True).tolist()
            self.paths = np.load(Config.PATHS_PATH, allow_pickle=True).tolist()
            self.ntotal = self.index.ntotal
            
            print(f"Index & metadata loaded. ntotal = {self.ntotal}")
        except Exception as e:
            print(f" Error loading FAISS: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int) -> tuple:
        """Search for similar images"""
        k = max(1, min(int(k), self.ntotal))
        D, I = self.index.search(query_embedding, k)
        return D, I
    
    def get_label(self, idx: int) -> str:
        """Get label for index"""
        return str(self.labels[idx])
    
    def get_path(self, idx: int) -> str:
        """Get path for index"""
        return str(self.paths[idx])
