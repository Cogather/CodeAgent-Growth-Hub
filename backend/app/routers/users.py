from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import require_admin
from app.models import SysUser
from app.schemas import (
    SysUserCreate,
    SysUserCreateResponse,
    SysUserItem,
    SysUserListResponse,
    SysUserResetPasswordResponse,
    SysUserUpdate,
)
from app.services.password import generate_temporary_password, hash_password

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


def _format_dt(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _to_item(user: SysUser) -> SysUserItem:
    return SysUserItem(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
        created_at=_format_dt(user.created_at),
        updated_at=_format_dt(user.updated_at),
    )


@router.get("", response_model=SysUserListResponse)
def list_users(db: Session = Depends(get_db)):
    users = db.query(SysUser).order_by(SysUser.id).all()
    return SysUserListResponse(items=[_to_item(user) for user in users])


@router.post("", response_model=SysUserCreateResponse)
def create_user(payload: SysUserCreate, db: Session = Depends(get_db)):
    username = payload.username.strip()
    if db.query(SysUser).filter(SysUser.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    temp_password = payload.password or generate_temporary_password()
    user = SysUser(
        username=username,
        name=payload.name.strip(),
        password_hash=hash_password(temp_password),
        role=payload.role,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return SysUserCreateResponse(user=_to_item(user), temporary_password=temp_password)


@router.put("/{user_id}", response_model=SysUserItem)
def update_user(
    user_id: int,
    payload: SysUserUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(require_admin),
):
    user = db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        if user.id == current_user.id and not payload.is_active:
            raise HTTPException(status_code=400, detail="不能禁用当前登录账号")
        user.is_active = payload.is_active
    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)
    return _to_item(user)


@router.post("/{user_id}/reset-password", response_model=SysUserResetPasswordResponse)
def reset_user_password(user_id: int, db: Session = Depends(get_db)):
    user = db.get(SysUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    temp_password = generate_temporary_password()
    user.password_hash = hash_password(temp_password)
    user.must_change_password = True
    user.updated_at = datetime.now()
    db.commit()
    return SysUserResetPasswordResponse(temporary_password=temp_password)
