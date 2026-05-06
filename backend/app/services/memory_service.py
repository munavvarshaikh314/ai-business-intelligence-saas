from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.conversation_memory_model import ConversationMemory


class MemoryService:

    @staticmethod
    def get_memory(user_id: str, session_id: str):
        db: Session = SessionLocal()

        mem = db.query(ConversationMemory).filter(
            ConversationMemory.user_id == user_id,
            ConversationMemory.session_id == session_id
        ).first()

        if not mem:
            return None

        return mem.summary