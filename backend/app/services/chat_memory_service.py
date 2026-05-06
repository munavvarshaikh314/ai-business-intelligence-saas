from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.chat_message_model import ChatMessage


class ChatMemoryService:

    @staticmethod
    def get_recent_history(session_id: str, limit: int = 6) -> str:
        """
        Returns last N messages in a formatted string.
        """
        db: Session = SessionLocal()

        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        # Reverse to get correct order
        messages = list(reversed(messages))

        history_lines = []
        for msg in messages:
            role = "User" if msg.sender == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.message_text}")

        return "\n".join(history_lines)