import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user_model import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    # ---------------------------
    # Password Hashing
    # ---------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    # ---------------------------
    # JWT Token Creation
    # ---------------------------
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()

        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    # ---------------------------
    # Register User
    # ---------------------------
    @staticmethod
    def register(payload, db: Session):

        user_exists = db.query(User).filter(User.email == payload.email).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = AuthService.hash_password(payload.password)

        new_user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User registered successfully"}

    # ---------------------------
    # Login User
    # ---------------------------
    @staticmethod
    def login(payload, db: Session):

        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not AuthService.verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = AuthService.create_access_token({"user_id": str(user.id)})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    # ---------------------------
    # Verify Token
    # ---------------------------
    @staticmethod
    def verify_token(token: str, db: Session):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id")

            if user_id is None:
                return None

            user = db.query(User).filter(User.id == user_id).first()
            return user

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None