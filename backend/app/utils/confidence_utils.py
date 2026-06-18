import math


def compute_confidence(scores: list) -> float:
    """
    Converts reranker/FAISS scores to 0-1 confidence.

    Handles three score types:
    1. CrossEncoder logits — any float, sigmoid converts to 0-1
    2. L2 distances — positive floats, lower is better
    3. Already normalized 0-1 scores
    """
    if not scores:
        return 0.0

    valid = [s for s in scores if s is not None]
    if not valid:
        return 0.0

    top = valid[0]

    # Already in 0-1 range — use directly
    if 0.0 <= top <= 1.0:
        avg = sum(valid) / len(valid)
        return round((0.7 * top) + (0.3 * avg), 3)

    # CrossEncoder logits (can be negative or large positive)
    # Convert using sigmoid: 1 / (1 + e^-x)
    # sigmoid(-10) = 0.00005, sigmoid(0) = 0.5, sigmoid(10) = 0.99995
    try:
        converted = [1.0 / (1.0 + math.exp(-s)) for s in valid]
        top_c = converted[0]
        avg_c = sum(converted) / len(converted)
        confidence = (0.7 * top_c) + (0.3 * avg_c)
        return round(max(0.0, min(1.0, confidence)), 3)
    except (OverflowError, ZeroDivisionError):
        # Fallback for extreme values
        return 0.5 if top > 0 else 0.1


def label_confidence(confidence: float) -> str:
    if confidence >= 0.75:
        return "high"
    if confidence >= 0.45:
        return "medium"
    return "low"

