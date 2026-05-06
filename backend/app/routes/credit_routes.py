from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.credit_service import CreditService

router = APIRouter()

@router.get("/me")
def get_my_credits(current_user=Depends(get_current_user)):
    credit = CreditService.get_or_create_credit(current_user.id)
    return {"credits": credit.credits}