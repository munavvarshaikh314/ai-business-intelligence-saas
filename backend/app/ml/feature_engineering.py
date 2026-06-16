import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def detect_target_type(y: pd.Series) -> str:
    if y.dtype == "object":
        return "classification"
    if y.nunique() <= 10:
        return "classification"
    return "regression"


def auto_detect_target_column(df: pd.DataFrame) -> tuple[str, str]:
    """
    Automatically detect the best target column and task type.
    Priority: numeric columns with names like sales, revenue, churn, price, profit.
    Returns (target_column, task_type)
    """
    sales_keywords = ["sales", "revenue", "profit", "price", "amount", "total", "income", "cost"]
    churn_keywords = ["churn", "attrition", "left", "exited", "cancelled", "churned"]
    classification_keywords = ["status", "category", "class", "label", "type", "flag"]

    cols_lower = {col: col.lower() for col in df.columns}

    # Check churn/classification first
    for col, lower in cols_lower.items():
        if any(k in lower for k in churn_keywords):
            return col, "classification"

    # Check numeric sales/regression targets
    for col, lower in cols_lower.items():
        if any(k in lower for k in sales_keywords):
            if pd.api.types.is_numeric_dtype(df[col]):
                return col, "regression"

    # Check classification keywords
    for col, lower in cols_lower.items():
        if any(k in lower for k in classification_keywords):
            return col, "classification"

    # Fallback: pick last numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        col = numeric_cols[-1]
        task = detect_target_type(df[col])
        return col, task

    raise ValueError("Could not auto-detect a suitable target column from the CSV.")


def preprocess_dataframe(df: pd.DataFrame, target_col: str):
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe")

    df = df.copy()

    # Drop date-like columns — not useful for sklearn without encoding
    for col in df.columns:
        if col == target_col:
            continue
        if df[col].dtype == "object":
            try:
                pd.to_datetime(df[col], errors="raise")
                df = df.drop(columns=[col])
            except Exception:
                pass

    df = df.dropna(subset=[target_col])

    y = df[target_col]
    X = df.drop(columns=[target_col])

    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    # Need at least 10 rows to split
    if len(X) < 10:
        return X, X, y, y
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


# import pandas as pd
# from sklearn.model_selection import train_test_split


# def detect_target_type(y: pd.Series):
#     """
#     Detect whether target is regression or classification.
#     """
#     if y.dtype == "object":
#         return "classification"

#     unique_values = y.nunique()

#     # if only few unique values -> classification
#     if unique_values <= 10:
#         return "classification"

#     return "regression"


# def preprocess_dataframe(df: pd.DataFrame, target_col: str):
#     """
#     Splits into X and y, handles missing values, returns X, y.
#     """
#     if target_col not in df.columns:
#         raise ValueError(f"Target column '{target_col}' not found in dataframe")

#     df = df.copy()

#     # Drop rows where target is missing
#     df = df.dropna(subset=[target_col])

#     y = df[target_col]
#     X = df.drop(columns=[target_col])

#     return X, y


# def split_data(X, y, test_size=0.2, random_state=42):
#     return train_test_split(X, y, test_size=test_size, random_state=random_state)