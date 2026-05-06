from fastapi.responses import StreamingResponse
from app.services.rag_answer_service import RAGAnswerService
from app.services.chat_memory_service import ChatMemoryService

@router.get("/stream/{dataset_id}/{session_id}")
def stream_answer(dataset_id: str, session_id: str, question: str, current_user=Depends(get_current_user)):

    def generator():
        # use memory + rewrite + retrieval
        chat_history = ChatMemoryService.get_recent_history(session_id, limit=6)

        rewritten_query = question  # optional rewrite later
        retrieved = RAGService.retrieve(dataset_id, user_id, rewritten_query, top_k=5)

        chunks = retrieved.get("chunks", [])
        context = "\n\n".join(chunks)

        prompt = f"""
Answer ONLY using context.

Context:
{context}

Question:
{question}

Answer:
"""

        for token in LLMService.stream_text(prompt):
            yield token

    return StreamingResponse(generator(), media_type="text/plain")