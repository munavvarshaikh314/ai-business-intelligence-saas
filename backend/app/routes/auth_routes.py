from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()


class UpdateProfileRequest(BaseModel):
    name: str


class UpdatePreferencesRequest(BaseModel):
    language: str = "en"
    region: str = "India"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register(payload, db)

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(payload, db)

@router.get("/me", response_model=UserResponse)
def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.put("/update-profile", response_model=UserResponse)
def update_profile(
    payload: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.merge(current_user)
    user.name = payload.name.strip()
    db.commit()
    db.refresh(user)
    return user


@router.put("/update-preferences")
def update_preferences(payload: UpdatePreferencesRequest, current_user=Depends(get_current_user)):
    return {
        "message": "Preferences saved",
        "preferences": {
            "language": payload.language,
            "region": payload.region,
        }
    }


@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.merge(current_user)
    if not AuthService.verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    user.password_hash = AuthService.hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
