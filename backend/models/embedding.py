"""
DINOv2 Embedding Model for image feature extraction
"""
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import json
import os
from config import Config


class DinoEmbeddingNet(nn.Module):
    """DINOv2 backbone with projection head"""
    def __init__(self, backbone, proj_dim=128):
        super().__init__()
        self.backbone = backbone
        self.proj_head = nn.Linear(backbone.embed_dim, proj_dim)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.proj_head(x)
        return x


class EmbeddingModel:
    """Wrapper for DINOv2 embedding model"""
    
    def __init__(self):
        self.model = None
        self.device = None
        self.transform = None
        self.emb_dim = 128
    
    def load(self):
        """Load model architecture and weights from bundle"""
        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {self.device}")
            
            # Load architecture config
            arch_path = Config.MODEL_ARCH_PATH
            print(f"Loading architecture from {arch_path}...")
            with open(arch_path, 'r') as f:
                arch_config = json.load(f)
            
            backbone_name = arch_config.get('backbone', 'dinov2_vitb14_reg')
            self.emb_dim = arch_config.get('embedding_dim', 128)
            
            print(f"  Backbone: {backbone_name}")
            print(f"  Embedding dim: {self.emb_dim}")
            
            # Load DINOv2 backbone
            print(f"Loading {backbone_name} backbone...")
            backbone = torch.hub.load('facebookresearch/dinov2', backbone_name)
            
            # Create model with projection head
            self.model = DinoEmbeddingNet(backbone, proj_dim=self.emb_dim)
            
            # Load trained weights
            weights_path = Config.MODEL_WEIGHTS_PATH
            print(f"Loading trained weights from {weights_path}...")
            if os.path.exists(weights_path):
                checkpoint = torch.load(weights_path, map_location=self.device)
                # Handle different naming conventions: 'fc' vs 'proj_head'
                if 'fc.weight' in checkpoint and 'proj_head.weight' not in checkpoint:
                    checkpoint['proj_head.weight'] = checkpoint.pop('fc.weight')
                    checkpoint['proj_head.bias'] = checkpoint.pop('fc.bias')
                self.model.load_state_dict(checkpoint, strict=False)
                print(f"  Weights loaded successfully")
            else:
                print(f"  Weights file not found at {weights_path}")
                print(f"  Using pretrained backbone only")
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Setup transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
            
            print(f"Model loaded successfully (embedding dim: {self.emb_dim})")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def encode(self, pil_img: Image.Image) -> np.ndarray:
        """Encode an image to embedding"""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # Transform and encode
            img_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(img_tensor)
            
            # Normalize and return as numpy (2D array: 1 x emb_dim)
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
            return embedding.cpu().numpy()
            
        except Exception as e:
            print(f"Error encoding image: {e}")
            raise
