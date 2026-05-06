from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.chat_session_model import ChatSession
from app.models.chat_message_model import ChatMessage
from app.models.dataset_model import Dataset

from app.services.sql_answer_service import SQLAnswerService
from app.services.rag_answer_service import RAGAnswerService
from app.services.prediction_answer_service import PredictionAnswerService
from app.services.usage_log_service import UsageLogService
from app.services.memory_summarizer_service import MemorySummarizerService
from app.security.prompt_injection_guard import PromptInjectionGuard
from app.security.dataset_guard import DatasetGuard
from app.services.query_router_service import QueryRouterService

class ChatService:

    @staticmethod
    def create_session(dataset_id: str, user_id: str, session_name: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        session = ChatSession(
            user_id=user_id,
            dataset_id=dataset_id,
            session_name=session_name
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return {"session_id": str(session.id)}

    @staticmethod
    def get_sessions(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.dataset_id == dataset_id
        ).all()

    @staticmethod
    def get_messages(session_id: str, user_id: str):
        db: Session = SessionLocal()
        # Auto update memory after every 10 messages
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()

        if msg_count % 10 == 0:
            MemorySummarizerService.summarize_session(user_id, session_id)

        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        return messages

    

    @staticmethod
    def ask(dataset_id: str, user_id: str, session_id: str, question: str):
        DatasetGuard.check_access(user_id, dataset_id)

        question = PromptInjectionGuard.sanitize(question)
        if PromptInjectionGuard.is_malicious(question):
            raise HTTPException(status_code=400, detail="Potential prompt injection detected.")

        db: Session = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.dataset_id == dataset_id
            ).first()

            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")

            db.add(ChatMessage(session_id=session_id, sender="user", message_text=question))
            db.commit()
        finally:
            db.close()

        query_type = QueryRouterService.detect_query_type(question)
        try:
            if query_type == "SQL":
                result = SQLAnswerService.answer(dataset_id, user_id, question)
            elif query_type == "PREDICTION":
                result = PredictionAnswerService.answer(dataset_id, user_id, question)
            else:
                result = RAGAnswerService.answer(dataset_id, user_id, session_id, question)
        except HTTPException as exc:
            result = {
                "answer": exc.detail,
                "confidence": 0.0,
                "query_type": query_type,
                "sources": [],
            }
        except Exception as exc:
            result = {
                "answer": f"I could not complete that request: {str(exc)}",
                "confidence": 0.0,
                "query_type": query_type,
                "sources": [],
            }

        db = SessionLocal()
        try:
            db.add(ChatMessage(
                session_id=session_id,
                sender="assistant",
                message_text=result.get("answer", "")
            ))
            db.commit()
        finally:
            db.close()

        try:
            UsageLogService.log_usage(
                user_id=user_id,
                dataset_id=dataset_id,
                session_id=session_id,
                query_type=query_type,
                question=question,
                prompt_tokens=0,
                completion_tokens=0,
            )
        except Exception:
            pass

        return result

    @staticmethod
    def delete_session(session_id: str, user_id: str):
        db: Session = SessionLocal()

        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        db.delete(session)
        db.commit()

        return {"message": "Chat session deleted"}
