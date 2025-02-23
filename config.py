import os

# Get the API host from environment variable or use default for local development
WS_API_URL = os.getenv('WS_API_URL', 'ws://localhost:8000') 