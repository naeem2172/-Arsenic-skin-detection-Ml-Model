# Arsenic Awareness Chatbot - Setup Guide

## Prerequisites

- Python 3.10 or 3.11 (TensorFlow compatibility)
- 4GB+ RAM recommended (for sentence-transformers model)

## Installation

1. Navigate to the main project and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the chatbot knowledge base (first run downloads ~500MB embedding model):
   ```bash
   cd arsenic_awareness_chatbot
   python scripts/init_database.py
   ```

3. Optional: Add GEMINI_API_KEY to `.env` for enhanced AI responses

## Running with Flask App

The chatbot is integrated into the main Arsenic Detection app. Simply run:

```bash
python app.py
```

Then visit http://localhost:5000/chatbot

## Standalone Mode

Run the Streamlit app:
```bash
streamlit run arsenic_awareness_chatbot/standalone_app/streamlit_app.py
```

Or the FastAPI backend:
```bash
uvicorn arsenic_awareness_chatbot.backend_api.main:app --port 8000
```
