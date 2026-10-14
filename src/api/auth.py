from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_user_permission_codes
from src.db.session import get_db
from src.models.entities import User
from src.models.schemas import (
    LoginRequest,
    MeResponse,
    ProfileUpdateRequest,
    TokenResponse,
    UserResponse,
)
from src.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(request.email).lower()))
    if user is None or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoặc mật khẩu không đúng")
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=user)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeResponse:
    """Thông tin + danh sách quyền của tài khoản đang đăng nhập.

    FE dùng `permissions` để ẩn/hiện menu. Admin trả về toàn bộ quyền.
    """
    return MeResponse(
        user=UserResponse.model_validate(user),
        permissions=sorted(get_user_permission_codes(db, user)),
    )


@router.patch("/me", response_model=UserResponse)
def update_me(
    request: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Sale/Admin tự sửa profile cá nhân (không đổi được role/quyền)."""
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.phone is not None:
        user.phone = request.phone
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    if request.title is not None:
        user.title = request.title
    if request.password is not None:
        user.password_hash = hash_password(request.password)
    db.commit()
    db.refresh(user)
    return user
