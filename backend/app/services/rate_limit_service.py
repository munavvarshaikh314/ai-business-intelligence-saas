import time
import redis
from fastapi import HTTPException
from app.config import settings


r = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)


class RateLimitService:

    @staticmethod
    def check_limit(user_id: str, limit: int = 20, window_seconds: int = 60):
        """
        20 requests per minute per user.
        """
        key = f"rate_limit:{user_id}"

        current = r.get(key)

        if current is None:
            r.set(key, 1, ex=window_seconds)
            return True

        if int(current) >= limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

        r.incr(key)
        return True