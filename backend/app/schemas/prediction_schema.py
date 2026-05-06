from pydantic import BaseModel
from typing import Optional


class SalesPredictionRequest(BaseModel):
    month: str
    marketing_spend: Optional[float] = None


class SalesPredictionResponse(BaseModel):
    prediction: float
    confidence: Optional[float] = None


class ChurnPredictionRequest(BaseModel):
    tenure: int
    monthly_charges: float
    contract_type: str


class ChurnPredictionResponse(BaseModel):
    churn_probability: float