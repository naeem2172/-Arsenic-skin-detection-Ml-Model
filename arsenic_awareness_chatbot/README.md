# Arsenic Awareness Chatbot

Multilingual (English/Bangla) chatbot for arsenic poisoning awareness and skin detection guidance. Uses **Ollama** – free, local, no API key needed.

## Setup

1. **Install Ollama** (free, no API key)
   - Download from [ollama.com](https://ollama.com/download)
   - Run: `ollama pull llama3.2`

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running

**Integration with Arsenic Detection Flask app:**
The chatbot is integrated into the main Arsenic Detection web app. Run the Flask app and visit the Chatbot page.

**Standalone FastAPI backend:**
```bash
uvicorn backend_api.main:app --reload --port 8000
```

## API Endpoints

- `POST /api/chat` - Send message, get response
- `GET /health` - Health check

## Project Structure

- `core/` - Chatbot logic, language detection
- `backend_api/` - FastAPI server
- `integration_examples/` - React, HTML, WordPress examples
