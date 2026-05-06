from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.credit_service import CreditService

router = APIRouter()

@router.post("/add-credits/{user_id}")
def add_credits(user_id: str, amount: int, current_user=Depends(get_current_user)):
    # later restrict only admin
    credit = CreditService.add_credits(user_id, amount)
    return {"message": "Credits added", "credits": credit.credits}