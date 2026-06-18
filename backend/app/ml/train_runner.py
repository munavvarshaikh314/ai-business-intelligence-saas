from app.ml.train_sales_model import train_sales_model
from app.ml.train_churn_model import train_churn_model
from app.services.logging_service import LoggingService



if __name__ == "__main__":
    LoggingService.info("Starting model training pipeline...")
    
    LoggingService.info("Training Sales Model...")
    result = train_sales_model("app/storage/uploads/sales.csv", target_col="Revenue")
    LoggingService.info(result)

    LoggingService.info("Training Churn Model...")
    result = train_churn_model("app/storage/uploads/churn.csv", target_col="Churn")
    LoggingService.info(result)