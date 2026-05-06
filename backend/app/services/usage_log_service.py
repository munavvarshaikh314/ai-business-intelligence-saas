from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.usage_log_model import UsageLog


class UsageLogService:

    @staticmethod
    def log_usage(
        user_id: str,
        dataset_id: str,
        session_id: str,
        query_type: str,
        question: str,
        prompt_tokens: int,
        completion_tokens: int
    ):
        db: Session = SessionLocal()

        total_tokens = prompt_tokens + completion_tokens

        log = UsageLog(
            user_id=user_id,
            dataset_id=dataset_id,
            session_id=session_id,
            query_type=query_type,
            question=question,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_estimate=0
        )

        db.add(log)
        db.commit()

        return log