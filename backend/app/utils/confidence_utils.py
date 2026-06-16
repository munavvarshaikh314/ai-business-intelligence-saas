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

# def compute_confidence(scores: list[float]) -> float:
#     """
#     Computes a 0.0 - 1.0 confidence score from FAISS L2 distances.
#     In FAISS L2, a LOWER score means a BETTER match.
#     """
#     if not scores:
#         return 0.0

#     # 1. FAISS returns L2 distances. The first one is the best (lowest).
#     best_distance = scores[0]
#     avg_distance = sum(scores) / len(scores)

#     # 2. Convert L2 Distances into standard 0.0 to 1.0 confidence percentages
#     # We use 1 / (1 + distance) so 0.0 becomes 1.0 (100%), and higher distances drop toward 0
#     top_confidence = 1.0 / (1.0 + best_distance)
#     avg_confidence = 1.0 / (1.0 + avg_distance)

#     # 3. Calculate ambiguity (gap). 
#     # If the top match is 90% and average is 40%, the gap is huge (good!). 
#     # If top is 90% and average is 88%, the document has too many similar conflicting answers.
#     gap = top_confidence - avg_confidence

#     # 4. Final blended score (70% weight to the best match, 30% weight to how uniquely it stands out)
#     final_confidence = (0.7 * top_confidence) + (0.3 * max(0, gap))

#     # 5. Clamp between 0 and 1 just in case
#     if final_confidence < 0:
#         final_confidence = 0.0
#     if final_confidence > 1:
#         final_confidence = 1.0

#     print(f"[DEBUG] Best L2: {best_distance:.3f} | Top Conf: {top_confidence:.3f} | Final Blended Conf: {final_confidence:.3f}")

#     return round(final_confidence, 3)


# def label_confidence(score: float) -> str:
#     """
#     Converts numeric confidence score into readable label.
#     """

#     if score >= 0.85:
#         return "HIGH"

#     if score >= 0.60:
#         return "MEDIUM"

#     if score >= 0.35:
#         return "LOW"

#     return "VERY_LOW"