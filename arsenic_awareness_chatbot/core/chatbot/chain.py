"""Chatbot for arsenic awareness - Ollama (free, local)."""
import json
import urllib.request
from typing import Dict
from ..language.detector import LanguageDetector
from ..config.settings import settings
from ..config.prompts import get_system_prompt
from .memory import ConversationMemory


class ArsenicChatbot:
    """Chatbot powered by Ollama (free local LLM, no API key needed)."""

    def __init__(self):
        self.memory = ConversationMemory()

    def _generate_response(self, message: str, lang: str, session_id: str) -> str:
        """Generate response using Ollama API."""
        try:
            system_prompt = get_system_prompt(lang)
            history = self.memory.get_history(session_id)

            parts = [f"{system_prompt}\n\n"]
            for h in history:
                prefix = "User: " if h["role"] == "user" else "Assistant: "
                parts.append(f"{prefix}{h['content']}\n\n")
            parts.append("Assistant:")

            prompt = "".join(parts)

            url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": settings.TEMPERATURE,
                    "num_predict": settings.MAX_TOKENS,
                },
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
            return (result.get("response") or "").strip()
        except urllib.error.URLError as e:
            if "Connection refused" in str(e) or "nodename nor servname" in str(e).lower():
                return (
                    "Ollama is not running. To use the chatbot for free:\n"
                    "1. Install Ollama from https://ollama.com/download\n"
                    "2. Run: ollama pull llama3.2\n"
                    "3. Start Ollama (it runs in the background)\n"
                    "4. Refresh this page and try again."
                )
            return f"Could not connect to Ollama: {e.reason}. Make sure Ollama is running."
        except Exception as e:
            return f"Sorry, the chatbot is temporarily unavailable: {str(e)}. Make sure Ollama is running and the model is pulled (ollama pull {settings.OLLAMA_MODEL})."

    def chat(self, message: str, session_id: str = "default") -> Dict:
        """Process chat message and return response."""
        try:
            lang = LanguageDetector.detect(message)
            self.memory.add(session_id, "user", message)

            response_text = self._generate_response(message, lang, session_id)

            disclaimer = settings.DISCLAIMER_BN if lang == "bn" else settings.DISCLAIMER_EN
            full_response = f"{response_text}\n\n_{disclaimer}_"

            self.memory.add(session_id, "assistant", full_response)

            return {
                "response": full_response,
                "language": lang,
                "sources": [],
            }
        except Exception as e:
            return {
                "response": f"Sorry, an error occurred: {str(e)}. Please try again.",
                "language": "en",
                "sources": [],
            }
