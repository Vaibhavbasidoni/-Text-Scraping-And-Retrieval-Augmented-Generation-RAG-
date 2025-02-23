from dotenv import load_dotenv
import os

# Load environment variables at the start
load_dotenv()

from fastapi import FastAPI, WebSocket
from .scraper import NewsArticleScraper
from .rag_pipeline import RAGPipeline
import logging
import json
from typing import List, Dict
import asyncio
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize components
scraper = NewsArticleScraper()
rag = RAGPipeline()
documents: List[Dict] = []

@app.on_event("startup")
async def startup_event():
    global documents
    try:
        # Fetch initial articles
        documents = scraper.scrape_articles()
        # Process documents through RAG pipeline
        await rag.process_documents(documents)
        logger.info(f"Initialized with {len(documents)} documents")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        documents = []

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "RAG Chat API is running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Receive message
            query = await websocket.receive_text()
            logger.info(f"Received query: {query}...")

            try:
                # Generate response
                response = await rag.generate_response(query)
                
                # Send response in chunks
                chunk_size = 100
                words = response.split()
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i + chunk_size])
                    await websocket.send_text(chunk)
                    await asyncio.sleep(0.1)  # Small delay between chunks
                
                # Send end marker
                await websocket.send_text("[END]")
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                await websocket.send_text(f"Sorry, an error occurred: {str(e)}")
                await websocket.send_text("[END]")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass  # Ignore errors during close

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",  # Listen on all available interfaces
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )