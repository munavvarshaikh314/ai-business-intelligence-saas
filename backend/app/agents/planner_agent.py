from app.services.llm import LLMService


class PlannerAgent:

    @staticmethod
    def plan(query: str, memory_summary: str = None):

        memory_block = memory_summary if memory_summary else "No memory available."

        prompt = f"""
You are a planning agent.

You have access to long-term memory summary from previous conversation.

Memory Summary:
{memory_block}

Now classify the user query into the best tool.

TOOLS:
- RAG (documents, PDFs)
- SQL (analytics, numbers, database)
- ML (prediction, forecasting)

Return JSON ONLY:

{{
  "intent": "RAG | SQL | ML",
  "reason": "...",
  "needs_verification": true/false
}}

Query: {query}
"""

        result = LLMService.generate_text(prompt)
        return result["text"]