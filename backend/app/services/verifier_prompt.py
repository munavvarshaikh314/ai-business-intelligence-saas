def build_verifier_prompt(context: str, question: str, answer: str):
    return f"""
You are a strict fact-checking verifier.

Task:
Check whether the assistant's answer is fully supported by the context.

Rules:
- Only use the context.
- If answer contains anything not in context -> UNSUPPORTED.
- If context contains conflicting statements -> CONFLICT.
- If context supports answer -> SUPPORTED.

Return output ONLY as JSON in this format:

{{
  "verdict": "SUPPORTED" | "UNSUPPORTED" | "CONFLICT",
  "confidence": 0.0 to 1.0,
  "reason": "short reason"
}}

Context:
{context}

User Question:
{question}

Assistant Answer:
{answer}

JSON:
"""