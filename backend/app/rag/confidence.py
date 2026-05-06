def compute_confidence(distances: list) -> float:
    """
    Confidence score based on FAISS L2 distances.
    Lower distance = higher confidence.
    """

    if not distances:
        return 0.0

    best = distances[0]

    # distance thresholds (tunable)
    if best < 0.4:
        return 0.95
    if best < 0.8:
        return 0.85
    if best < 1.2:
        return 0.70
    if best < 1.8:
        return 0.55

    return 0.40