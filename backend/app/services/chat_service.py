from fastapi import HTTPException
from numpy import e
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.chat_session_model import ChatSession
from app.models.chat_message_model import ChatMessage
from app.models.dataset_model import Dataset
from app.models.document_chunk_model import DocumentChunk
from app.models.dataset_column_model import DatasetColumn  # ← FIXED: was missing

from app.services.sql_answer_service import SQLAnswerService
from app.services.rag_answer_service import RAGAnswerService
from app.services.prediction_answer_service import PredictionAnswerService
from app.services.usage_log_service import UsageLogService
from app.services.memory_summarizer_service import MemorySummarizerService
from app.security.prompt_injection_guard import PromptInjectionGuard
from app.security.dataset_guard import DatasetGuard
from app.services.query_router_service import QueryRouterService
from app.services.logging_service import LoggingService


class ChatService:

    @staticmethod
    def has_indexed_pdf_content(dataset_id: str) -> bool:
        db: Session = SessionLocal()
        try:
            return db.query(DocumentChunk).filter(
                DocumentChunk.dataset_id == dataset_id
            ).first() is not None
        finally:
            db.close()

    @staticmethod
    def should_prefer_rag(question: str, has_pdf_content: bool) -> bool:
        if not has_pdf_content:
         return False

        q = question.lower()

    # ONLY override to RAG for explicit document-reading phrases
    # Never override for analytics/SQL questions
        explicit_doc_terms = [
        "according to", "from the document", "from the pdf",
        "what does it say", "policy says", "document says",
        "my resume", "my cv", "my profile", "my background",
        "mentioned in", "written in", "stated in",
        "from the file", "in the document", "the document states",
        "as per the", "as mentioned", "refer to the",
        
       ]
        return any(term in q for term in explicit_doc_terms)

    @staticmethod
    def create_session(dataset_id: str, user_id: str, session_name: str):
        db: Session = SessionLocal()
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_sessions(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            return db.query(ChatSession).filter(
                ChatSession.user_id == user_id,
                ChatSession.dataset_id == dataset_id
            ).all()
        finally:
            db.close()

    @staticmethod
    def get_messages(session_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()

            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")

            msg_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).count()

            if msg_count > 0 and msg_count % 10 == 0:
                try:
                    MemorySummarizerService.summarize_session(user_id, session_id)
                except Exception:
                    pass

            return db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).all()
        finally:
            db.close()

    @staticmethod
    def ask(dataset_id: str, user_id: str, session_id: str, question: str, mode: str = None):
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

            db.add(ChatMessage(
                session_id=session_id,
                sender="user",
                message_text=question
            ))
            db.commit()
        finally:
            db.close()

        has_pdf_content = ChatService.has_indexed_pdf_content(dataset_id)
        requested_mode = (mode or "").upper()
        query_type = (
            requested_mode
            if requested_mode in {"RAG", "SQL", "PREDICTION"}
            else QueryRouterService.detect_query_type(question)
        )
        if ChatService.should_prefer_rag(question, has_pdf_content):
            query_type = "RAG"

        try:
            if query_type == "SQL":
                try:
                    result = SQLAnswerService.answer(dataset_id, user_id, question)
                    LoggingService.info("SQL SUCCESS")
                except HTTPException as exc:
                    LoggingService.error(f"SQL FAILED: {exc.detail}")
                    raise HTTPException(
                    status_code=400,
                     detail="Could not answer this data question. Please try rephrasing or select CSV/SQL mode."
    )

                    if has_pdf_content:
                        query_type = "RAG"
                        result = RAGAnswerService.answer(dataset_id, user_id, session_id, question)
                    else:
                        raise
            elif query_type == "PREDICTION":
                result = PredictionAnswerService.answer(dataset_id, user_id, question)
            else:
                result = RAGAnswerService.answer(dataset_id, user_id, session_id, question)

        except HTTPException as exc:
            result = {
        "answer": str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        "confidence": 0.0,
        "query_type": query_type,
        "sources": [],
    }
        except Exception as exc:
            import traceback
            LoggingService.error(f"FULL TRACE: {traceback.format_exc()}")
            LoggingService.error(f"Unexpected error: {type(exc).__name__}: {exc}")
            result = {
        "answer": "I could not complete that request. Please try again.",
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
                query_type=result.get("query_type", query_type),
                question=question,
                prompt_tokens=result.get("prompt_tokens", 0),
                completion_tokens=result.get("completion_tokens", 0),
            )
        except Exception:
            pass

        return result

    @staticmethod
    def get_suggested_questions(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            dataset_type = dataset.dataset_type or "CSV"

            if dataset_type == "PDF":
                return {
                    "dataset_type": "PDF",
                    "suggested_questions": [
                        "What is this document about?",
                        "Summarize the key points of this document.",
                        "What are the main rules or policies mentioned?",
                        "Are there any deadlines or dates mentioned?",
                        "What actions are required according to this document?",
                    ]
                }

            # CSV — generate questions based on actual column names
            columns = db.query(DatasetColumn).filter(
                DatasetColumn.dataset_id == dataset_id
            ).all()

            col_names = [c.column_name for c in columns]

            numeric_keywords = ["sales", "revenue", "profit", "cost", "price", "amount", "quantity", "total", "score"]
            date_keywords = ["date", "month", "year", "time", "period", "day"]
            category_keywords = ["region", "category", "type", "department", "product", "status", "class", "segment"]

            has_numeric = any(any(k in c.lower() for k in numeric_keywords) for c in col_names)
            has_date = any(any(k in c.lower() for k in date_keywords) for c in col_names)
            has_category = any(any(k in c.lower() for k in category_keywords) for c in col_names)

            numeric_col = next(
                (c for c in col_names if any(k in c.lower() for k in numeric_keywords)),
                col_names[0] if col_names else "value"
            )
            cat_col = next(
                (c for c in col_names if any(k in c.lower() for k in category_keywords)),
                None
            )

            questions = []

            if has_numeric:
                questions.append(f"What is the total {numeric_col}?")
                questions.append(f"What is the average {numeric_col}?")

            if has_category and cat_col and has_numeric:
                questions.append(f"Which {cat_col} has the highest {numeric_col}?")
                questions.append(f"Show {numeric_col} broken down by {cat_col}.")

            if has_date and has_numeric:
                questions.append(f"Show the {numeric_col} trend over time.")

            if has_numeric:
                questions.append(f"Predict the {numeric_col} for next month.")

            if len(questions) < 4:
                questions += [
                    "Show me a summary of this dataset.",
                    "What are the top 5 records by value?",
                    "How many rows does this dataset have?",
                    "What are the column names and data types?",
                ]

            return {
                "dataset_type": "CSV",
                "columns": col_names,
                "suggested_questions": questions[:6],
            }

        finally:
            db.close()

    @staticmethod
    def delete_session(session_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()

            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")

            db.delete(session)
            db.commit()
            return {"message": "Chat session deleted"}
        finally:
            db.close()


# from fastapi import HTTPException
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.models.chat_session_model import ChatSession
# from app.models.chat_message_model import ChatMessage
# from app.models.dataset_model import Dataset
# from app.models.document_chunk_model import DocumentChunk
# from app.models.dataset_column_model import DatasetColumn

# from app.services.sql_answer_service import SQLAnswerService
# from app.services.rag_answer_service import RAGAnswerService
# from app.services.prediction_answer_service import PredictionAnswerService
# from app.services.usage_log_service import UsageLogService
# from app.services.memory_summarizer_service import MemorySummarizerService
# from app.security.prompt_injection_guard import PromptInjectionGuard
# from app.security.dataset_guard import DatasetGuard
# from app.services.query_router_service import QueryRouterService

# class ChatService:
#     @staticmethod
#     def has_indexed_pdf_content(dataset_id: str) -> bool:
#         db: Session = SessionLocal()
#         try:
#             return db.query(DocumentChunk).filter(DocumentChunk.dataset_id == dataset_id).first() is not None
#         finally:
#             db.close()

#     @staticmethod
#     def should_prefer_rag(question: str, has_pdf_content: bool) -> bool:
#         if not has_pdf_content:
#             return False

#         q = question.lower()
#         document_terms = [
#             "pdf", "document", "file", "resume", "cv", "profile", "candidate",
#             "experience", "skills", "education", "qualification", "project",
#             "certificate", "certification", "email", "phone", "contact",
#             "mentioned", "written", "uploaded", "about me", "according",
#         ]
#         return any(term in q for term in document_terms)

#     @staticmethod
#     def create_session(dataset_id: str, user_id: str, session_name: str):
#         db: Session = SessionLocal()

#         dataset = db.query(Dataset).filter(
#             Dataset.id == dataset_id,
#             Dataset.user_id == user_id
#         ).first()

#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         session = ChatSession(
#             user_id=user_id,
#             dataset_id=dataset_id,
#             session_name=session_name
#         )

#         db.add(session)
#         db.commit()
#         db.refresh(session)

#         return {"session_id": str(session.id)}

#     @staticmethod
#     def get_sessions(dataset_id: str, user_id: str):
#         db: Session = SessionLocal()
#         return db.query(ChatSession).filter(
#             ChatSession.user_id == user_id,
#             ChatSession.dataset_id == dataset_id
#         ).all()

#     @staticmethod
#     def get_messages(session_id: str, user_id: str):
#         db: Session = SessionLocal()
#         # Auto update memory after every 10 messages
#         msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()

#         session = db.query(ChatSession).filter(
#             ChatSession.id == session_id,
#             ChatSession.user_id == user_id
#         ).first()

#         if not session:
#             raise HTTPException(status_code=404, detail="Chat session not found")

#         if msg_count > 0 and msg_count % 10 == 0:
#             try:
#                 MemorySummarizerService.summarize_session(user_id, session_id)
#             except Exception:
#                 pass

#         messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
#         return messages

    

#     @staticmethod
#     def ask(dataset_id: str, user_id: str, session_id: str, question: str, mode: str = None):
#         DatasetGuard.check_access(user_id, dataset_id)

#         question = PromptInjectionGuard.sanitize(question)
#         if PromptInjectionGuard.is_malicious(question):
#             raise HTTPException(status_code=400, detail="Potential prompt injection detected.")

#         db: Session = SessionLocal()
#         try:
#             session = db.query(ChatSession).filter(
#                 ChatSession.id == session_id,
#                 ChatSession.user_id == user_id,
#                 ChatSession.dataset_id == dataset_id
#             ).first()

#             if not session:
#                 raise HTTPException(status_code=404, detail="Chat session not found")

#             db.add(ChatMessage(session_id=session_id, sender="user", message_text=question))
#             db.commit()
#         finally:
#             db.close()

#         has_pdf_content = ChatService.has_indexed_pdf_content(dataset_id)
#         requested_mode = (mode or "").upper()
#         query_type = requested_mode if requested_mode in {"RAG", "SQL", "PREDICTION"} else QueryRouterService.detect_query_type(question)
#         if ChatService.should_prefer_rag(question, has_pdf_content):
#             query_type = "RAG"

#         try:
#             if query_type == "SQL":
#                 try:
#                     result = SQLAnswerService.answer(dataset_id, user_id, question)
#                 except HTTPException:
#                     if has_pdf_content:
#                         query_type = "RAG"
#                         result = RAGAnswerService.answer(dataset_id, user_id, session_id, question)
#                     else:
#                         raise
#             elif query_type == "PREDICTION":
#                 result = PredictionAnswerService.answer(dataset_id, user_id, question)
#             else:
#                 result = RAGAnswerService.answer(dataset_id, user_id, session_id, question)
#         except HTTPException as exc:
#             result = {
#                 "answer": exc.detail,
#                 "confidence": 0.0,
#                 "query_type": query_type,
#                 "sources": [],
#             }
#         except Exception as exc:
#             result = {
#                 "answer": f"I could not complete that request: {str(exc)}",
#                 "confidence": 0.0,
#                 "query_type": query_type,
#                 "sources": [],
#             }

#         db = SessionLocal()
#         try:
#             db.add(ChatMessage(
#                 session_id=session_id,
#                 sender="assistant",
#                 message_text=result.get("answer", "")
#             ))
#             db.commit()
#         finally:
#             db.close()

#         try:
#             UsageLogService.log_usage(
#                 user_id=user_id,
#                 dataset_id=dataset_id,
#                 session_id=session_id,
#                 query_type=result.get("query_type", query_type),
#                 question=question,
#                 prompt_tokens=0,
#                 completion_tokens=0,
#             )
#         except Exception:
#             pass

#         return result
    
#     @staticmethod
#     def get_suggested_questions(dataset_id: str, user_id: str):
#         """
#         Returns suggested questions for onboarding based on dataset columns.
#         CSV datasets get analytics questions.
#         PDF datasets get document Q&A questions.
#         """
        
#         db: Session = SessionLocal()
#         try:
#             dataset = db.query(Dataset).filter(
#                 Dataset.id == dataset_id,
#                 Dataset.user_id == user_id
#             ).first()

#             if not dataset:
#                 raise HTTPException(status_code=404, detail="Dataset not found")

#             dataset_type = dataset.dataset_type or "CSV"

#             if dataset_type == "PDF":
#                 return {
#                     "dataset_type": "PDF",
#                     "suggested_questions": [
#                         "What is this document about?",
#                         "Summarize the key points of this document.",
#                         "What are the main rules or policies mentioned?",
#                         "Are there any deadlines or dates mentioned?",
#                         "What actions are required according to this document?",
#                     ]
#                 }

#             # For CSV — generate questions based on actual column names
#             columns = db.query(DatasetColumn).filter(
#                 DatasetColumn.dataset_id == dataset_id
#             ).all()

#             col_names = [c.column_name for c in columns]

#             # Build smart questions based on column name patterns
#             questions = []

#             numeric_keywords = ["sales", "revenue", "profit", "cost", "price", "amount", "quantity", "total", "score"]
#             date_keywords = ["date", "month", "year", "time", "period", "day"]
#             category_keywords = ["region", "category", "type", "department", "product", "status", "class", "segment"]

#             has_numeric = any(any(k in c.lower() for k in numeric_keywords) for c in col_names)
#             has_date = any(any(k in c.lower() for k in date_keywords) for c in col_names)
#             has_category = any(any(k in c.lower() for k in category_keywords) for c in col_names)

#             if has_numeric:
#                 numeric_col = next((c for c in col_names if any(k in c.lower() for k in numeric_keywords)), col_names[0])
#                 questions.append(f"What is the total {numeric_col}?")
#                 questions.append(f"What is the average {numeric_col}?")

#             if has_category:
#                 cat_col = next((c for c in col_names if any(k in c.lower() for k in category_keywords)), None)
#                 if cat_col and has_numeric:
#                     questions.append(f"Which {cat_col} has the highest {numeric_col if has_numeric else 'value'}?")
#                     questions.append(f"Show me {numeric_col if has_numeric else 'results'} broken down by {cat_col}.")

#             if has_date and has_numeric:
#                 questions.append(f"Show the {numeric_col if has_numeric else 'trend'} over time.")

#             if has_numeric:
#                 questions.append(f"Predict the {numeric_col} for next month.")

#             # Fallback generic questions
#             if len(questions) < 4:
#                 questions += [
#                     "Show me a summary of this dataset.",
#                     "What are the top 5 records by value?",
#                     "How many rows does this dataset have?",
#                     "What are the column names and data types?",
#                 ]

#             return {
#                 "dataset_type": "CSV",
#                 "columns": col_names,
#                 "suggested_questions": questions[:6],
#             }

#         finally:
#             db.close()

#     @staticmethod
#     def delete_session(session_id: str, user_id: str):
#         db: Session = SessionLocal()

#         session = db.query(ChatSession).filter(
#             ChatSession.id == session_id,
#             ChatSession.user_id == user_id
#         ).first()

#         if not session:
#             raise HTTPException(status_code=404, detail="Chat session not found")

#         db.delete(session)
#         db.commit()

#         return {"message": "Chat session deleted"}

