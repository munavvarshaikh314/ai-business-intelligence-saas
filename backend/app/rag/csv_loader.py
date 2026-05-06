import pandas as pd
from typing import List, Dict
from app.rag.text_cleaner import clean_text


def load_csv(file_path: str, max_rows: int = 5000) -> List[Dict]:
    """
    Converts CSV rows into text chunks for embeddings.
    Each row becomes a document-style text.
    """
    df = pd.read_csv(file_path)

    if df.empty:
        return []

    if len(df) > max_rows:
        df = df.head(max_rows)

    records = []
    for idx, row in df.iterrows():
        row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        row_text = clean_text(row_text)

        records.append({
            "row_index": idx,
            "text": row_text
        })

    return records