from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 150) -> List[Dict]:
    """
    Returns list of dict chunks:
    [
        { "chunk_index": 0, "text": "..."},
        ...
    ]
    """

    if not text:
        return []

    words = text.split()
    chunks = []

    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words)

        chunks.append({
            "chunk_index": chunk_index,
            "text": chunk_text_value
        })

        chunk_index += 1
        start += chunk_size - overlap

    return chunks