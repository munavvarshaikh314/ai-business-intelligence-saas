from app.services.llm_service import LLMService
from app.services.query_rewrite_prompt import build_rewrite_prompt


class QueryRewriteService:

    @staticmethod
    def rewrite(chat_history: str, question: str) -> str:
        prompt = build_rewrite_prompt(chat_history, question)
        rewritten = LLMService.generate_text(prompt)

        rewritten = rewritten.replace('"', '').strip()

        # If LLM returns empty, fallback
        if not rewritten:
            return question

        return rewritten