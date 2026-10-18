"""Xác thực JWT cho trang admin."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.entities import User
from src.services.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload.get("type", "admin") != "admin":
            raise ValueError("not an admin token")
        user_id = int(payload.get("sub", ""))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_error from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user
