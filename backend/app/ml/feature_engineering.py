import pandas as pd
from sklearn.model_selection import train_test_split


def detect_target_type(y: pd.Series):
    """
    Detect whether target is regression or classification.
    """
    if y.dtype == "object":
        return "classification"

    unique_values = y.nunique()

    # if only few unique values -> classification
    if unique_values <= 10:
        return "classification"

    return "regression"


def preprocess_dataframe(df: pd.DataFrame, target_col: str):
    """
    Splits into X and y, handles missing values, returns X, y.
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe")

    df = df.copy()

    # Drop rows where target is missing
    df = df.dropna(subset=[target_col])

    y = df[target_col]
    X = df.drop(columns=[target_col])

    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    return train_test_split(X, y, test_size=test_size, random_state=random_state)