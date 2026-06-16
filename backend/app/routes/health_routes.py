from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.config import settings
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


@router.get("/llm")
def llm_health():
    return {
        "provider": settings.LLM_PROVIDER,
        "gemini_model": settings.GEMINI_MODEL,
        "openai_model": settings.OPENAI_MODEL,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
    }
