from app.services.rag_service import RAGService
from app.services.llm import LLMService
from app.services.chat_memory_service import ChatMemoryService
from app.services.query_rewrite_service import QueryRewriteService
from app.utils.confidence_utils import compute_confidence, label_confidence
from app.services.usage_log_service import UsageLogService


CONFIDENCE_THRESHOLD = 0.05


class RAGAnswerService:
    @staticmethod
    def answer(dataset_id: str, user_id: str, session_id: str, question: str):
        chat_history = ChatMemoryService.get_recent_history(session_id, limit=6)
        if "Assistant:" in chat_history:
            rewritten_query = QueryRewriteService.rewrite(chat_history, question)
        else:
            rewritten_query = question

        retrieved = RAGService.retrieve(dataset_id, user_id, rewritten_query, top_k=5)
        chunks = retrieved.get("chunks", [])
        scores = retrieved.get("scores", [])
        sources = retrieved.get("sources", [])
        confidence = compute_confidence(scores)

        if not chunks:
            return {
                "answer": "I could not find relevant information in the document to answer this question.",
                "confidence": 0.0,
                "confidence_label": "low",
                "guardrail": "no_context",
                "sources": [],
                "query_type": "RAG",
                "rewritten_query": rewritten_query,
            }

        context = "\n\n".join(chunks)
        low_retrieval_confidence = confidence < CONFIDENCE_THRESHOLD

        prompt = f"""You are a precise document assistant.

Rules:
- Answer ONLY using the context below.
- If the answer is not in the context, say: "This information is not available in the document."
- Do not use external knowledge.
- Be concise and direct.

Context:
{context}

Question:
{question}

Answer:"""

        result = LLMService.generate_text_with_usage(prompt)
        answer = result["text"]
        prompt_tokens = result["prompt_tokens"]
        completion_tokens = result["completion_tokens"]

        final_confidence = round(confidence, 3)

        try:
            UsageLogService.log_usage(
                user_id=user_id,
                dataset_id=dataset_id,
                session_id=session_id,
                query_type="RAG",
                question=question,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        except Exception:
            pass

        guardrail = "low_confidence" if low_retrieval_confidence or final_confidence < 0.3 else None

        return {
            "answer": answer,
            "confidence": final_confidence,
            "confidence_label": label_confidence(final_confidence),
            "guardrail": guardrail,
            "sources": sources,
            "query_type": "RAG",
            "rewritten_query": rewritten_query,
            "verdict": "SUPPORTED",
            "reason": "Generated from retrieved document context.",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
