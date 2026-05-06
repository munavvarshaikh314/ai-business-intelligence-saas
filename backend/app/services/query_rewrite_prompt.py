def build_rewrite_prompt(chat_history: str, question: str):
    return f"""
You are a query rewriting assistant.

Task:
Rewrite the user question into a standalone search query.
Use chat history to resolve pronouns like "it", "that", "this", "they".

Rules:
- Output only the rewritten query text.
- Do NOT answer the question.
- Keep it short and retrieval-friendly.

Chat History:
{chat_history}

User Question:
{question}

Standalone Query:
"""