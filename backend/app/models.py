from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DEPT_LEVELS = 7


class MetaDepartment(Base):
    """部门树 — dept_code 为主键，parent_dept_code 关联上级，供各模块筛选"""

    __tablename__ = "meta_department"
    __table_args__ = (UniqueConstraint("parent_dept_code", "name", name="uq_dept_parent_name"),)

    dept_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    parent_dept_code: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("meta_department.dept_code", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    parent: Mapped[Optional["MetaDepartment"]] = relationship(
        "MetaDepartment", remote_side=[dept_code], back_populates="children"
    )
    children: Mapped[list["MetaDepartment"]] = relationship(
        "MetaDepartment", back_populates="parent"
    )


class MetaFocusPdu(Base):
    """重点关注 PDU — 组织树固定层级（默认第 4 层）节点，供全局视角筛选"""

    __tablename__ = "meta_focus_pdu"

    dept_code: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("meta_department.dept_code", ondelete="CASCADE"),
        primary_key=True,
    )
    alias: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class MetaPersonnel(Base):
    """人员名单 — 工号主键，七级部门名称/编码平铺存储"""

    __tablename__ = "meta_personnel"

    emp_no: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    name_initial: Mapped[str] = mapped_column(String(8), nullable=False)
    dept_l1_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l1_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l2_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l2_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l3_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l3_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l4_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l4_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l5_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l5_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l6_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l6_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    dept_l7_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    dept_l7_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class _PermZoneMixin:
    """区域权限白名单公共字段"""

    __abstract__ = True

    emp_no: Mapped[str] = mapped_column(String(64), primary_key=True)
    models: Mapped[str] = mapped_column(String(512), nullable=False)


class PermZoneYellow(Base, _PermZoneMixin):
    __tablename__ = "perm_zone_yellow"


class PermZoneBlue(Base, _PermZoneMixin):
    __tablename__ = "perm_zone_blue"


class PermZoneGreen(Base, _PermZoneMixin):
    __tablename__ = "perm_zone_green"


class StatUsage(Base):
    """使用统计 — 工号与使用次数，仅通过 Excel 导入刷新"""

    __tablename__ = "stat_usage"

    emp_no: Mapped[str] = mapped_column(String(64), primary_key=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class SysUser(Base):
    """系统登录账号 — 与业务人员名单独立管理"""

    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    must_change_password: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

