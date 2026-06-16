from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.dependencies import get_current_user
from app.schemas.chat_schema import CreateSessionRequest, AskRequest
from app.services.chat_service import ChatService
from app.services.export_service import ExportService
from app.services.rag_service import RAGService
from app.services.chat_memory_service import ChatMemoryService
from app.services.llm_service import LLMService

router = APIRouter()


# ── Session Management ─────────────────────────────────────

@router.post("/session/{dataset_id}")
def create_session(dataset_id: str, payload: CreateSessionRequest, current_user=Depends(get_current_user)):
    return ChatService.create_session(dataset_id, current_user.id, payload.session_name)


@router.get("/sessions/{dataset_id}")
def get_sessions(dataset_id: str, current_user=Depends(get_current_user)):
    return ChatService.get_sessions(dataset_id, current_user.id)


@router.get("/messages/{session_id}")
def get_messages(session_id: str, current_user=Depends(get_current_user)):
    return ChatService.get_messages(session_id, current_user.id)


@router.delete("/session/{session_id}")
def delete_session(session_id: str, current_user=Depends(get_current_user)):
    return ChatService.delete_session(session_id, current_user.id)


# ── Main Chat Endpoint ─────────────────────────────────────

@router.post("/ask/{dataset_id}")
def ask_question(dataset_id: str, payload: AskRequest, current_user=Depends(get_current_user)):
    return ChatService.ask(dataset_id, current_user.id, payload.session_id, payload.question, payload.mode)


# ── Streaming Endpoint (kept from original) ────────────────

@router.get("/stream/{dataset_id}/{session_id}")
def stream_answer(
    dataset_id: str,
    session_id: str,
    question: str,
    current_user=Depends(get_current_user)
):
    user_id = str(current_user.id)

    def generator():
        chat_history = ChatMemoryService.get_recent_history(session_id, limit=6)
        retrieved = RAGService.retrieve(dataset_id, user_id, question, top_k=5)
        chunks = retrieved.get("chunks", [])
        context = "\n\n".join(chunks)

        prompt = f"""Answer ONLY using the context below.
If the answer is not in the context, say: "This information is not available in the document."

Context:
{context}

Question:
{question}

Answer:"""

        for token in LLMService.stream_text(prompt):
            yield token

    return StreamingResponse(generator(), media_type="text/plain")


# ── Onboarding ─────────────────────────────────────────────

@router.get("/onboarding/suggested-questions/{dataset_id}")
def get_suggested_questions(dataset_id: str, current_user=Depends(get_current_user)):
    """Returns suggested questions based on dataset type and columns."""
    return ChatService.get_suggested_questions(dataset_id, current_user.id)


# ── Export ─────────────────────────────────────────────────

@router.post("/export/pdf/{session_id}")
def export_chat_as_pdf(session_id: str, current_user=Depends(get_current_user)):
    """Export full chat session as downloadable PDF."""
    pdf_bytes = ExportService.export_session_pdf(session_id, current_user.id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=chat_export_{session_id[:8]}.pdf"
        }
    )

# from fastapi import APIRouter, Depends
# from app.dependencies import get_current_user
# from app.schemas.chat_schema import CreateSessionRequest, AskRequest
# from app.services.chat_service import ChatService

# router = APIRouter()

# @router.post("/session/{dataset_id}")
# def create_session(dataset_id: str, payload: CreateSessionRequest, current_user=Depends(get_current_user)):
#     return ChatService.create_session(dataset_id, current_user.id, payload.session_name)

# @router.get("/sessions/{dataset_id}")
# def get_sessions(dataset_id: str, current_user=Depends(get_current_user)):
#     return ChatService.get_sessions(dataset_id, current_user.id)

# @router.get("/messages/{session_id}")
# def get_messages(session_id: str, current_user=Depends(get_current_user)):
#     return ChatService.get_messages(session_id, current_user.id)

# @router.post("/ask/{dataset_id}")
# def ask_question(dataset_id: str, payload: AskRequest, current_user=Depends(get_current_user)):
#     return ChatService.ask(dataset_id, current_user.id, payload.session_id, payload.question, payload.mode)

# @router.delete("/session/{session_id}")
# def delete_session(session_id: str, current_user=Depends(get_current_user)):
#     return ChatService.delete_session(session_id, current_user.id)
