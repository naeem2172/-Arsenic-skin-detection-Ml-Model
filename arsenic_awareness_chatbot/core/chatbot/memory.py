"""Conversation memory per session."""
from typing import List, Dict
from collections import defaultdict


class ConversationMemory:
    """In-memory conversation history per session."""

    def __init__(self, max_history: int = 10):
        self._sessions: Dict[str, List[Dict]] = defaultdict(list)
        self.max_history = max_history

    def add(self, session_id: str, role: str, content: str):
        """Add message to session."""
        self._sessions[session_id].append({"role": role, "content": content})
        if len(self._sessions[session_id]) > self.max_history * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history * 2 :]

    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for session."""
        return self._sessions[session_id][-self.max_history * 2 :]

    def clear(self, session_id: str):
        """Clear session history."""
        self._sessions[session_id] = []
