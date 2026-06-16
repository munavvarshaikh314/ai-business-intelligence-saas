from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.payment_model import Payment
from app.models.usage_log_model import UsageLog
from app.models.user_credit_model import UserCredit
from app.models.user_model import User
from app.services.credit_service import CreditService

router = APIRouter()


class UpdateCreditsRequest(BaseModel):
    credits: int


def require_admin(current_user=Depends(get_current_user)):
    if (current_user.role or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/bootstrap-status")
def bootstrap_status(db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(User.role.ilike("admin")).first() is not None
    return {"admin_exists": admin_exists}


@router.post("/bootstrap-first-admin")
def bootstrap_first_admin(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(User.role.ilike("admin")).first() is not None
    if admin_exists:
        raise HTTPException(status_code=403, detail="An admin user already exists")

    user = db.merge(current_user)
    user.role = "admin"
    db.commit()
    db.refresh(user)

    return {
        "message": "First admin created",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@router.get("/users")
def get_users(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    credits = db.query(UserCredit).all()
    credit_map = {str(row.user_id): row.credits for row in credits}

    return [
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "credits": credit_map.get(str(user.id), 0),
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.put("/users/{user_id}/credits")
def set_user_credits(
    user_id: str,
    payload: UpdateCreditsRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    if payload.credits < 0:
        raise HTTPException(status_code=400, detail="Credits cannot be negative")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
    if not credit:
        credit = UserCredit(user_id=user_id, credits=payload.credits)
        db.add(credit)
    else:
        credit.credits = payload.credits

    db.commit()
    db.refresh(credit)
    return {"message": "Credits updated", "user_id": str(user.id), "credits": credit.credits}


@router.post("/add-credits/{user_id}")
def add_credits(
    user_id: str,
    amount: int,
    current_user=Depends(require_admin),
):
    credit = CreditService.add_credits(user_id, amount)
    return {"message": "Credits added", "credits": credit.credits}


@router.get("/payments")
def get_payments(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(Payment, User)
        .join(User, Payment.user_id == User.id)
        .order_by(Payment.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": str(payment.id),
            "user_id": str(user.id),
            "user_email": user.email,
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "amount": payment.amount,
            "amount_paid": payment.amount / 100,
            "currency": "INR",
            "credits_added": payment.credits_added,
            "status": payment.status,
            "created_at": payment.created_at,
        }
        for payment, user in rows
    ]


@router.get("/usage-logs")
def get_usage_logs(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(UsageLog, User)
        .join(User, UsageLog.user_id == User.id)
        .order_by(UsageLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": str(log.id),
            "user_id": str(user.id),
            "user_email": user.email,
            "endpoint": log.query_type,
            "query_type": log.query_type,
            "question": log.question,
            "tokens_used": log.total_tokens,
            "credits_used": log.cost_estimate,
            "created_at": log.created_at,
        }
        for log, user in rows
    ]
