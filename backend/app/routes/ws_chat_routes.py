from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.utils.ws_auth_utils import get_user_id_from_ws
from app.database import SessionLocal
from app.models.chat_message_model import ChatMessage
from app.services.chat_memory_service import ChatMemoryService
from app.services.query_rewrite_service import QueryRewriteService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.utils.confidence_utils import compute_confidence
from app.services.logging_service import LoggingService
router = APIRouter()


@router.websocket("/ws/chat/{dataset_id}/{session_id}")
async def websocket_chat(websocket: WebSocket, dataset_id: str, session_id: str):
    """
    WebSocket streaming chatbot endpoint.
    Frontend sends JSON: {"question": "..."}
    Backend streams tokens.
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question")

            if not question:
                await websocket.send_json({"error": "Question is required"})
                continue

            # ----------------------------
            # Chat history + query rewrite
            # ----------------------------
            chat_history = ChatMemoryService.get_recent_history(session_id, limit=6)
            rewritten_query = QueryRewriteService.rewrite(chat_history, question)

            user_id = get_user_id_from_ws(websocket)

            if not user_id:
                await websocket.send_json({"error": "Unauthorized"})
                await websocket.close()
                return

            # ----------------------------
            # Retrieve chunks
            # ----------------------------
            retrieved = RAGService.retrieve(dataset_id, user_id, rewritten_query, top_k=5)

            chunks = retrieved.get("chunks", [])
            scores = retrieved.get("scores", [])
            sources = retrieved.get("sources", [])

            confidence = compute_confidence(scores)

            if not chunks:
                await websocket.send_json({
                    "type": "final",
                    "payload": {
                        "answer": "No relevant context found in document.",
                        "confidence": 0.0,
                        "sources": []
                    }
                })
                continue

            context = "\n\n".join(chunks)

            prompt = f"""
You are a helpful AI assistant.
Answer ONLY using context.
If not found, say "Not found in document."

Context:
{context}

User Question:
{question}

Answer:
"""

            # ----------------------------
            # Stream token-by-token
            # ----------------------------
            full_answer = ""

            for token in LLMService.stream_text(prompt):
                full_answer += token
                await websocket.send_json({"type": "token", "data": token})

            # ----------------------------
            # Save message in DB
            # ----------------------------
            db: Session = SessionLocal()

            user_msg = ChatMessage(
                session_id=session_id,
                sender="user",
                message_text=question
            )

            assistant_msg = ChatMessage(
                session_id=session_id,
                sender="assistant",
                message_text=full_answer
            )

            db.add(user_msg)
            db.add(assistant_msg)
            db.commit()

            # ----------------------------
            # Send final response packet
            # ----------------------------
            await websocket.send_json({
                "type": "final",
                "payload": {
                    "answer": full_answer,
                    "confidence": confidence,
                    "sources": sources,
                    "rewritten_query": rewritten_query
                }
            })

    except WebSocketDisconnect:
        LoggingService.info("Client disconnected")
