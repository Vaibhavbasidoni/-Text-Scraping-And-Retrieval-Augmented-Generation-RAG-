# News Assistant Pro - RAG-based News Query System

## Overview
News Assistant Pro is an AI-powered news application that scrapes real-time news from Times of India, processes it using RAG (Retrieval-Augmented Generation), and provides contextual responses to user queries through an interactive interface.

## Project Structure
```
news-assistant/
├── app/
│   ├── api.py             # FastAPI WebSocket server for handling chat requests
│   ├── embeddings.py      # Handles text embeddings generation
│   ├── rag_pipeline.py    # Implements the RAG pipeline for query processing
│   ├── scheduler.py       # Manages periodic news updates
│   ├── scraper.py        # Scrapes news from RSS feeds
│   ├── update_documents.py # Updates document store with new articles
│   └── vector_store.py    # Manages vector database operations
└── ui/
    └── streamlit_app.py   # Streamlit frontend interface
```

## Core Components

### Backend Components

1. **api.py**
   - Implements FastAPI WebSocket server
   - Handles real-time chat communication
   - Manages request/response flow between frontend and RAG pipeline

2. **embeddings.py**
   - Generates text embeddings for news articles
   - Uses sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
   - Processes text for vector storage in Pinecone

3. **rag_pipeline.py**
   - Implements RAG (Retrieval-Augmented Generation)
   - Combines retrieved context with Google's Gemini LLM
   - Processes user queries with relevant news context

4. **scheduler.py**
   - Manages periodic news updates
   - Runs background tasks for RSS feed scraping
   - Ensures fresh news content every 30 minutes

5. **scraper.py**
   - Scrapes news from Times of India RSS feeds
   - Handles multiple news categories (Top Stories, World, Tech, Business, Sports)
   - Processes raw HTML content using feedparser

6. **update_documents.py**
   - Updates Pinecone with new articles
   - Manages document processing pipeline
   - Handles data persistence and updates

7. **vector_store.py**
   - Manages Pinecone vector database operations
   - Handles similarity search for relevant news
   - Stores and retrieves embeddings efficiently

### Frontend Component

8. **streamlit_app.py**
   - Provides user interface for news queries
   - Handles WebSocket communication with backend
   - Displays formatted responses with loading states

## Tech Stack

### Backend
- **FastAPI**: WebSocket server implementation
- **Sentence-Transformers**: Text embeddings (paraphrase-multilingual-MiniLM-L12-v2)
- **Google Gemini**: Large Language Model
- **Pinecone**: Vector database for similarity search
- **Beautiful Soup**: Web scraping
- **APScheduler**: Task scheduling
- **Langchain**: RAG pipeline implementation
- **Pydantic**: Data validation
- **WebSockets**: Real-time communication
- **Feedparser**: RSS feed parsing

### Frontend
- **Streamlit**: User interface
- **HTML/CSS**: Custom styling
- **WebSocket-client**: Real-time communication

### Data Sources
- Times of India RSS Feeds:
  - Top Stories
  - World News
  - Technology
  - Business
  - Sports

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

3. Launch the Streamlit interface:
```bash
streamlit run ui/streamlit_app.py
```

4. Access the application at: http://localhost:8501

## Usage
1. Enter news-related queries in the chat interface
2. System retrieves relevant news and generates responses
3. View formatted responses with context from recent news

## Sample Queries
- "What are today's top headlines?"
- "Show me the latest technology news"
- "What's happening in the business world?"
- "Give me recent sports updates"

## Streamlit Cloud Deployment
Access the live application at: [Your Streamlit Cloud URL]

## License
[Your chosen license]
