def build_conflict_prompt(context: str):
    return f"""
You are an AI contradiction detector.

Task:
Analyze the context and check if it contains contradictory statements.

Rules:
- If two parts disagree, mark as CONFLICT.
- If all statements align, mark as NO_CONFLICT.

Return ONLY JSON:

{{
  "conflict": true/false,
  "conflicting_points": ["point1", "point2"]
}}

Context:
{context}

JSON:
"""