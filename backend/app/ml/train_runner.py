from app.ml.train_sales_model import train_sales_model
from app.ml.train_churn_model import train_churn_model


if __name__ == "__main__":
    print("Training Sales Model...")
    result = train_sales_model("app/storage/uploads/sales.csv", target_col="Revenue")
    print(result)

    print("Training Churn Model...")
    result = train_churn_model("app/storage/uploads/churn.csv", target_col="Churn")
    print(result)