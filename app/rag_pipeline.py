from typing import List, Dict
import google.generativeai as genai
from .embeddings import EmbeddingsHandler
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        # Initialize Pinecone with existing index
        self.pc = Pinecone(
            api_key=os.getenv('PINECONE_API_KEY')
        )
        
        # Use existing index name
        self.index_name = "rag1"
        self.index = self.pc.Index(self.index_name)
        
        # Initialize embeddings handler
        self.embeddings_handler = EmbeddingsHandler()
        
        # Initialize Gemini with more specific instructions
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Store articles and last context in memory
        self.articles = {}
        self.last_context = []
        
        logger.info("Initialized RAG pipeline")

    async def process_documents(self, documents: List[Dict]) -> None:
        """Process and index documents"""
        try:
            # Clear memory cache
            self.articles.clear()
            self.last_context = []  # Clear last context when updating documents
            
            batch_size = 100
            vectors = []
            
            for i, doc in enumerate(documents):
                # Store article for quick retrieval
                doc_id = f"doc_{i}"
                self.articles[doc_id] = doc
                
                # Create document text with metadata
                text = f"Title: {doc['title']}\nContent: {doc['content']}\nTimestamp: {doc['timestamp']}"
                
                # Get embeddings
                embeddings = await self.embeddings_handler.get_embeddings([text])
                if embeddings:
                    # Prepare vector for batch upsert
                    vectors.append((doc_id, embeddings[0], {
                        "title": doc['title'],
                        "timestamp": doc['timestamp']
                    }))
                
                # Batch upsert when we reach batch_size
                if len(vectors) >= batch_size:
                    self.index.upsert(vectors=vectors)
                    vectors = []
            
            # Upsert any remaining vectors
            if vectors:
                self.index.upsert(vectors=vectors)
                    
            logger.info(f"Indexed {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            raise

    async def generate_response(self, query: str) -> str:
        """Generate response using RAG"""
        try:
            # Get query embedding
            query_embedding = await self.embeddings_handler.get_embeddings([query])
            if not query_embedding:
                return "Sorry, I couldn't process your query."
                
            # Search for relevant documents
            search_results = self.index.query(
                vector=query_embedding[0],
                top_k=5,  # Increased from 3 to 5 for more context
                include_metadata=True
            )
            
            # Build new context
            new_context = []
            seen_titles = set()  # Track unique titles
            
            for match in search_results.matches:
                if match.id in self.articles:
                    article = self.articles[match.id]
                    if article['title'] not in seen_titles:  # Avoid duplicates
                        new_context.append(f"Title: {article['title']}\nContent: {article['content']}")
                        seen_titles.add(article['title'])
            
            if not new_context:
                return "I don't have enough information to answer that question."
            
            # Update last context
            self.last_context = new_context
            
            # Check if query is asking for details about a specific topic
            is_detail_query = any(word in query.lower() for word in ['detail', 'more', 'specific'])
            
            # Build prompt
            prompt = f"""Based on the following news articles, answer the question: {query}

Context:
{'-' * 80}
{'\n\n'.join(new_context)}
{'-' * 80}

Important instructions:
1. Only use information explicitly stated in the provided context
2. If the query asks for details about a specific topic and that topic isn't in the context, clearly state that
3. Be consistent with the information across responses
4. For detailed queries, provide all relevant information from the context
5. Format lists with numbers and bullet points for readability
6. If information appears contradictory, prioritize the most detailed source

Please provide a comprehensive answer following these instructions."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, an error occurred: {str(e)}" 