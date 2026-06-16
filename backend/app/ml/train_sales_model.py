# import os
import os
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor

from app.ml.feature_engineering import preprocess_dataframe, split_data
from app.ml.metrics import regression_metrics


MODEL_DIR = "app/storage/models"


def train_sales_model(csv_path: str, target_col: str, model_name="sales_model.pkl"):
    df = pd.read_csv(csv_path)

    X, y = preprocess_dataframe(df, target_col)
    X_train, X_test, y_train, y_test = split_data(X, y)

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "bool"]).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=200, random_state=42))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    metrics = regression_metrics(y_test, y_pred)

    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save pipeline
    model_path = os.path.join(MODEL_DIR, model_name)
    joblib.dump(pipeline, model_path)

    # Save feature metadata alongside model
    # This tells predictor exactly what columns + default values are needed
    feature_meta = {
        "feature_columns": X.columns.tolist(),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "defaults": {
            col: float(X[col].median()) if col in numeric_features
            else str(X[col].mode()[0]) if not X[col].mode().empty else ""
            for col in X.columns
        }
    }

    meta_path = model_path.replace(".pkl", "_meta.json")
    with open(meta_path, "w") as f:
        json.dump(feature_meta, f)

    return {
        "model_path": model_path,
        "metrics": metrics,
        "feature_columns": X.columns.tolist(),
    }


# import joblib
# import pandas as pd

# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import OneHotEncoder, StandardScaler
# from sklearn.ensemble import RandomForestRegressor

# from app.ml.feature_engineering import preprocess_dataframe, split_data
# from app.ml.metrics import regression_metrics


# MODEL_DIR = "app/storage/models"


# def train_sales_model(csv_path: str, target_col: str, model_name="sales_model.pkl"):
#     df = pd.read_csv(csv_path)

#     X, y = preprocess_dataframe(df, target_col)
#     X_train, X_test, y_train, y_test = split_data(X, y)

#     numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
#     categorical_features = X.select_dtypes(include=["object", "bool"]).columns.tolist()

#     numeric_transformer = Pipeline(steps=[
#         ("imputer", SimpleImputer(strategy="median")),
#         ("scaler", StandardScaler())
#     ])

#     categorical_transformer = Pipeline(steps=[
#         ("imputer", SimpleImputer(strategy="most_frequent")),
#         ("encoder", OneHotEncoder(handle_unknown="ignore"))
#     ])

#     preprocessor = ColumnTransformer(
#         transformers=[
#             ("num", numeric_transformer, numeric_features),
#             ("cat", categorical_transformer, categorical_features)
#         ]
#     )

#     model = RandomForestRegressor(
#         n_estimators=200,
#         random_state=42
#     )

#     pipeline = Pipeline(steps=[
#         ("preprocessor", preprocessor),
#         ("model", model)
#     ])

#     pipeline.fit(X_train, y_train)

#     y_pred = pipeline.predict(X_test)

#     metrics = regression_metrics(y_test, y_pred)

#     os.makedirs(MODEL_DIR, exist_ok=True)

#     model_path = os.path.join(MODEL_DIR, model_name)
#     joblib.dump(pipeline, model_path)

#     return {
#         "model_path": model_path,
#         "metrics": metrics
#     }