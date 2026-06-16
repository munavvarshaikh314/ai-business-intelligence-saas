import hashlib
import hmac
import secrets
import re

def hash_password(password: str) -> str:
    from passlib.context import CryptContext
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    from passlib.context import CryptContext
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return ctx.verify(plain, hashed)

def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r"[^\w\-_\.]", "_", filename)
    filename = filename.lstrip(".")
    return filename[:255]

def is_safe_sql_identifier(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))

def mask_email(email: str) -> str:
    parts = email.split("@")
    if len(parts) != 2:
        return "***"
    local = parts[0]
    masked = local[0] + "***" + local[-1] if len(local) > 2 else "***"
    return f"{masked}@{parts[1]}"
