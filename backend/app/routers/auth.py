from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps.auth import ACCESS_TOKEN_COOKIE, get_current_user
from app.models import SysUser
from app.schemas import AuthUser, ChangePasswordRequest, LoginRequest
from app.services.jwt_auth import create_access_token
from app.services.password import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_auth_user(user: SysUser) -> AuthUser:
    return AuthUser(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        must_change_password=user.must_change_password,
    )


def _set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_expire_hours * 3600,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE, path="/")


@router.post("/login", response_model=AuthUser)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    username = payload.username.strip()
    user = db.query(SysUser).filter(SysUser.username == username).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(user.id, user.username, user.role)
    _set_auth_cookie(response, token)
    return _to_auth_user(user)


@router.post("/logout", status_code=204)
def logout(response: Response):
    _clear_auth_cookie(response)


@router.get("/me", response_model=AuthUser)
def get_me(current_user: SysUser = Depends(get_current_user)):
    return _to_auth_user(current_user)


@router.post("/change-password", response_model=AuthUser)
def change_password(
    payload: ChangePasswordRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码不正确")
    if payload.old_password == payload.new_password:
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")

    current_user.password_hash = hash_password(payload.new_password)
    current_user.must_change_password = False
    current_user.updated_at = datetime.now()
    db.commit()
    db.refresh(current_user)
    return _to_auth_user(current_user)
