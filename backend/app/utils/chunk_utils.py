def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append((idx, chunk))
        idx += 1
        start += chunk_size - overlap

    return chunks