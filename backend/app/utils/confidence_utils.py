def compute_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0

    top = scores[0]
    avg = sum(scores) / len(scores)

    # gap helps detect ambiguity
    gap = top - avg

    confidence = (0.7 * top) + (0.3 * gap)

    if confidence < 0:
        confidence = 0.0
    if confidence > 1:
        confidence = 1.0

    return round(confidence, 3)