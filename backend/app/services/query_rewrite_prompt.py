def build_rewrite_prompt(chat_history, question: str) -> str:
    """
    Rewrites ambiguous follow-up questions into clear standalone questions.
    Works for any document type — resume, policy, report, etc.
    NEVER produces keyword lists — always produces a complete sentence.
    """

    # Build history string
    if isinstance(chat_history, str):
        history_text = chat_history.strip()
    elif isinstance(chat_history, list):
        history_text = ""
        for msg in chat_history[-3:]:
            sender = getattr(msg, "sender", "user")
            text = getattr(msg, "message_text", "")
            if text:
                history_text += f"{sender}: {text}\n"
        history_text = history_text.strip()
    else:
        history_text = ""

    if not history_text:
        # No history — return question unchanged
        return f"Return this question exactly as written:\n\n{question}"

    return f"""You are a search query clarification assistant.

Your ONLY job: rewrite the follow-up question into a clear, standalone question using context from the conversation.

STRICT RULES:
1. Output ONE complete sentence or question — nothing else
2. NEVER output a keyword list or comma-separated terms
3. NEVER expand the question into multiple topics
4. If the question is already clear and standalone, return it UNCHANGED
5. Only use information from the conversation history to resolve pronouns like "it", "they", "that"
6. Do NOT answer the question — only rewrite it

Examples of CORRECT rewrites:
- "what about skills?" + history about resume → "What skills are listed in the document?"
- "tell me more" + history about experience → "What work experience is described in the document?"
- "mention my skills" → "mention my skills" (already clear — return unchanged)

Examples of WRONG rewrites (never do this):
- "technical skills, programming languages, frontend, backend, databases" ← WRONG, keyword list
- "skills experience education projects certifications" ← WRONG, keyword list

Conversation history:
{history_text}

Follow-up question: {question}

Rewritten question (one sentence only):"""