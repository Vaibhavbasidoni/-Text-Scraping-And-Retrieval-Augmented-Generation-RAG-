from pinecone import Pinecone
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class PineconeManager:
    def __init__(self, index_name: str = "rag"):
        self.index_name = index_name
        
        # Initialize Pinecone with new method
        self.pc = Pinecone(
            api_key=os.getenv('PINECONE_API_KEY')
        )
        
        # Connect to existing index
        self.index = self.pc.Index(self.index_name)

    async def upsert_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        Upsert documents and their embeddings to Pinecone
        """
        try:
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # Ensure embedding length matches index dimensions (1536)
                if len(embedding) != 1536:
                    print(f"Warning: Embedding dimension mismatch. Expected 1536, got {len(embedding)}")
                    continue
                    
                vector = {
                    'id': f"doc_{i}",
                    'values': embedding,
                    'metadata': {
                        'title': doc['title'],
                        'content': doc['content'],
                        'url': doc['url'],
                        'timestamp': doc['timestamp']
                    }
                }
                vectors.append(vector)
            
            self.index.upsert(vectors=vectors)
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")

    async def query(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Query the vector store for similar documents
        """
        try:
            # Ensure query embedding length matches index dimensions
            if len(query_embedding) != 1536:
                raise ValueError(f"Query embedding dimension mismatch. Expected 1536, got {len(query_embedding)}")
                
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            return [match.metadata for match in results.matches]
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return [] 