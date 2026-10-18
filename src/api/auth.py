from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.models.entities import User
from src.models.schemas import LoginRequest, TokenResponse, UserResponse
from src.services.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(request.email).lower()))
    if user is None or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=user)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user
