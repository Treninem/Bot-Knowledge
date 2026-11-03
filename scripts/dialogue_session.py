"""Ephemeral chat session around the verified local conversation router.

Caller provides a separate instance per session. Only approved bot outputs are
kept in a bounded in-memory deque; user messages, identifiers and permissions
are never persisted or exported. A request to stop silences the session until
its owner explicitly calls reset().
"""
from __future__ import annotations

from collections import deque

from conversation_router import ConversationRouter

class DialogueSession:
    def __init__(self, router: ConversationRouter | None = None, *, history: int = 5):
        if not 1 <= history <= 20:
            raise ValueError("History bound must be between 1 and 20")
        self.router = router or ConversationRouter()
        self._recent: deque[str] = deque(maxlen=history)
        self._muted = False
        self._replies = 0

    @property
    def state(self) -> dict:
        # No user messages or bot response text in external state.
        return {"muted": self._muted, "recent_count": len(self._recent),
                "reply_count": self._replies}

    def respond(self, message: str, **kwargs) -> dict:
        if self._muted:
            return {"status": "session_silenced", "text": None}
        # Always supply session-managed recent responses.
        if "recent" in kwargs:
            raise ValueError("Recent replies managed by this session")
        result = self.router.reply(message, recent=tuple(self._recent), **kwargs)
        if result["status"] == "silence_requested":
            self._muted = True
        if result["status"] == "ok":
            self._recent.append(result["text"])
            self._replies += 1
        return result

    def reset(self) -> None:
        self._recent.clear()
        self._replies = 0
        self._muted = False
