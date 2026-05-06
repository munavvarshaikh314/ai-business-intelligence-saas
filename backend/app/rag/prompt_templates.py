def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
    context_text = ""

    for chunk in retrieved_chunks:
        context_text += f"\n[Chunk {chunk.get('chunk_index', '')}]\n{chunk.get('text', '')}\n"

    prompt = f"""
You are an AI BI assistant. Your job is to answer based ONLY on provided context.

Rules:
- If answer not in context, say: "I could not find this information in your dataset."
- Keep answer short, business-friendly, and accurate.
- If possible, include numeric values.

User Query:
{query}

Context:
{context_text}

Answer:
""".strip()

    return prompt