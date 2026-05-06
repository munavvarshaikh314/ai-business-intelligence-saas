import pandas as pd


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Example: create profit_margin if columns exist
    if "profit" in df.columns and "sales" in df.columns:
        df["profit_margin"] = df["profit"] / (df["sales"] + 1e-9)

    return df