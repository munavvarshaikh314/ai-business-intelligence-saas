from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.chat_memory_service import ChatMemoryService
from app.services.query_rewrite_service import QueryRewriteService
from app.utils.confidence_utils import compute_confidence

from app.services.verifier_service import VerifierService
from app.services.conflict_service import ConflictDetectionService


class RAGAnswerService:

    @staticmethod
    def answer(dataset_id: str, user_id: str, session_id: str, question: str):

        # ---------------------------
        # Memory + Query Rewrite
        # ---------------------------
        chat_history = ChatMemoryService.get_recent_history(session_id, limit=6)
        rewritten_query = QueryRewriteService.rewrite(chat_history, question)

        # ---------------------------
        # Retrieve chunks
        # ---------------------------
        retrieved = RAGService.retrieve(dataset_id, user_id, rewritten_query, top_k=5)

        chunks = retrieved.get("chunks", [])
        scores = retrieved.get("scores", [])
        sources = retrieved.get("sources", [])

        confidence = compute_confidence(scores)

        if not chunks:
            return {
                "answer": "No relevant context found in the document.",
                "confidence": 0.0,
                "sources": [],
                "query_type": "RAG",
                "rewritten_query": rewritten_query
            }

        # Build context
        context = "\n\n".join(chunks)

        # ---------------------------
        # Conflict Detection
        # ---------------------------
        conflict_result = ConflictDetectionService.detect(context)

        if conflict_result.get("conflict") is True:
            return {
                "answer": "⚠️ The document contains conflicting statements related to your question. Please verify manually.",
                "confidence": confidence,
                "sources": sources,
                "query_type": "RAG",
                "rewritten_query": rewritten_query,
                "conflict": True,
                "conflicting_points": conflict_result.get("conflicting_points", [])
            }
        


        if confidence < 0.35:
            return {
                "answer": "I could not find a confident answer in the document.",
                "confidence": confidence,
                "sources": sources,
                "query_type": "RAG",
                "rewritten_query": rewritten_query
            }

        # ---------------------------
        # Generate Answer (Strict grounding)
        # ---------------------------
        prompt = f"""
You are a helpful AI assistant.

Rules:
- Answer ONLY using the context.
- If not found, say: "Not found in document."
- Do not add external knowledge.
- Keep answer short and clear.

Context:
{context}

User Question:
{question}

Answer:
"""

        answer = LLMService.generate_text(prompt)

        # ---------------------------
        # Verify Answer
        # ---------------------------
        verify_result = VerifierService.verify(context, question, answer)

        verdict = verify_result.get("verdict", "UNSUPPORTED")
        verifier_confidence = verify_result.get("confidence", 0.0)

        if verdict == "UNSUPPORTED":
            return {
                "answer": "⚠️ I generated an answer, but it is not strongly supported by the document context.",
                "confidence": min(confidence, verifier_confidence),
                "sources": sources,
                "query_type": "RAG",
                "rewritten_query": rewritten_query,
                "verdict": verdict,
                "reason": verify_result.get("reason", "")
            }

        return {
            "answer": answer,
            "confidence": min(confidence, verifier_confidence),
            "sources": sources,
            "query_type": "RAG",
            "rewritten_query": rewritten_query,
            "verdict": verdict,
            "reason": verify_result.get("reason", "")
        }