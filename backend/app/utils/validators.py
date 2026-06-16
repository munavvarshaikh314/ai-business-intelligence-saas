import re
from typing import Optional

def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))

def is_strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    return True, "OK"

def is_valid_dataset_name(name: str) -> bool:
    return bool(name and len(name.strip()) >= 2 and len(name) <= 100)

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))

def is_valid_uuid(value: str) -> bool:
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(pattern, str(value).lower()))

def sanitize_query(query: str, max_length: int = 2000) -> str:
    query = query.strip()
    if len(query) > max_length:
        query = query[:max_length]
    return query
