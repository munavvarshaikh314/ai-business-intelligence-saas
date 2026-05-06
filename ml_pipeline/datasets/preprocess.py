import pandas as pd


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # remove empty columns
    df = df.dropna(axis=1, how="all")

    # fill missing numeric values
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        df[col] = df[col].fillna(df[col].median())

    # fill missing categorical values
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("UNKNOWN")

    return df