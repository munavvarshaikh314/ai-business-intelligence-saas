import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df = df.dropna(how="all")
    df = df.drop_duplicates()
    return df

def infer_date_columns(df: pd.DataFrame) -> List[str]:
    date_cols = []
    for col in df.columns:
        if any(kw in col.lower() for kw in ["date", "time", "month", "year", "day"]):
            try:
                pd.to_datetime(df[col], errors="raise")
                date_cols.append(col)
            except Exception:
                pass
    return date_cols

def infer_numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=[np.number]).columns.tolist()

def safe_json_serialize(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    return obj

def dataframe_to_safe_dict(df: pd.DataFrame) -> List[Dict]:
    records = df.to_dict(orient="records")
    return [{k: safe_json_serialize(v) for k, v in row.items()} for row in records]

def get_dataframe_summary(df: pd.DataFrame) -> Dict:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "numeric_columns": infer_numeric_columns(df),
        "date_columns": infer_date_columns(df),
        "null_counts": df.isnull().sum().to_dict(),
    }
