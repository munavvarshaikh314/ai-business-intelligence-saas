from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
def health_check():
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "OK", "db": "OK"}
    except:
        return {"status": "FAILED", "db": "FAILED"}