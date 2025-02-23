from sentence_transformers import SentenceTransformer
import torch
from typing import List
import logging
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingsHandler:
    def __init__(self):
        # Use a smaller model (about 500MB instead of 2.2GB)
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("Initialized embeddings model: paraphrase-multilingual-MiniLM-L12-v2")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        """
        try:
            # Generate embeddings
            with torch.no_grad():
                embeddings = self.model.encode(texts, normalize_embeddings=True)
                
            # Convert numpy float32 to Python float and ensure 1024 dimensions
            embeddings_list = [
                [float(val) for val in emb[:1024]]  # Convert each value to Python float
                for emb in embeddings
            ]
            
            # Pad if necessary
            for emb in embeddings_list:
                if len(emb) < 1024:
                    emb.extend([0.0] * (1024 - len(emb)))
            
            logger.info(f"Generated embeddings with dimension: {len(embeddings_list[0])}")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None 