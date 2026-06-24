from app.database import SessionLocal
from app.models.usage_log_model import UsageLog
from app.services.logging_service import LoggingService


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
        db = SessionLocal()
        try:
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

            # ← FIXED: deduct 1 credit per query
            try:
                from app.services.credit_service import CreditService
                CreditService.deduct_credits(user_id, amount=1)
            except Exception as credit_err:
                # Log but don't crash — usage is logged even if deduction fails
                LoggingService.warning(f"Credit deduction failed for {user_id}: {credit_err}")

            return log
        finally:
            db.close()


# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.models.usage_log_model import UsageLog
# from app.services.logging_service import LoggingService


# class UsageLogService:

#     @staticmethod
#     def log_usage(
#         user_id: str,
#         dataset_id: str,
#         session_id: str,
#         query_type: str,
#         question: str,
#         prompt_tokens: int,
#         completion_tokens: int
#     ):
#         db: Session = SessionLocal()
#         try:
#             total_tokens = prompt_tokens + completion_tokens

#             log = UsageLog(
#                 user_id=user_id,
#                 dataset_id=dataset_id,
#                 session_id=session_id,
#                 query_type=query_type,
#                 question=question,
#                 prompt_tokens=prompt_tokens,
#                 completion_tokens=completion_tokens,
#                 total_tokens=total_tokens,
#                 cost_estimate=0
#             )
#             db.add(log)
#             db.commit()

#             # ← FIXED: deduct 1 credit per query
#             try:
#                 from app.services.credit_service import CreditService
#                 CreditService.deduct_credits(user_id, amount=1)
#             except Exception as credit_err:
#                 # Log but don't crash — usage is logged even if deduction fails
#                 LoggingService.warning(f"Credit deduction failed for {user_id}: {credit_err}")

#             return log
#         finally:
#             db.close()
            
            
            
  