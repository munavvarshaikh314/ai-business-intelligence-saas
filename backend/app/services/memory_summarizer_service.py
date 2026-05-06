from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.chat_message_model import ChatMessage
from app.models.conversation_memory_model import ConversationMemory
from app.services.llm_service import LLMService


class MemorySummarizerService:

    @staticmethod
    def summarize_session(user_id: str, session_id: str, limit: int = 20):
        db: Session = SessionLocal()

        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        messages = list(reversed(messages))

        conversation_text = ""
        for msg in messages:
            role = "User" if msg.sender == "user" else "Assistant"
            conversation_text += f"{role}: {msg.message_text}\n"

        prompt = f"""
You are a memory summarizer agent.

Summarize this conversation in a compact way so that it can be reused as memory later.

Rules:
- Keep summary under 200 words
- Store important user goals, preferences, dataset context, decisions
- Ignore small talk

Conversation:
{conversation_text}

Final Summary:
"""

        result = LLMService.generate_text_with_usage(prompt)
        summary = result["text"]

        existing = db.query(ConversationMemory).filter(
            ConversationMemory.session_id == session_id,
            ConversationMemory.user_id == user_id
        ).first()

        if existing:
            existing.summary = summary
        else:
            mem = ConversationMemory(
                user_id=user_id,
                session_id=session_id,
                summary=summary
            )
            db.add(mem)

        db.commit()

        return summary