from app.services.llm_service import LLMService


class IntentRouter:

    @staticmethod
    def classify_intent(query: str):
        prompt = f"""
You are an AI routing system.

Classify the user query into ONLY ONE category:

1. RAG → if question is about PDF, documents, files, text explanation
2. SQL → if question is about structured data, analytics, tables, numbers
3. ML → if question is about prediction, forecasting, what-if analysis

Return ONLY ONE WORD:
RAG or SQL or ML

Query: {query}
"""

        result = LLMService.generate_text(prompt)
        return result["text"].strip().upper()