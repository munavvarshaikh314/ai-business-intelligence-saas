from app.services.llm_service import LLMService


class CriticAgent:

    @staticmethod
    def verify(query: str, answer: str):

        prompt = f"""
You are a critic AI.

Check if the answer is:
1. Correct
2. Grounded in context
3. Not hallucinated

Return JSON:

{{
  "valid": true/false,
  "score": 0-100,
  "reason": "..."
}}

Query: {query}
Answer: {answer}
"""

        result = LLMService.generate_text(prompt)
        return result["text"]