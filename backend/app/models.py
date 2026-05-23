from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DEPT_LEVELS = 7


class MetaDepartment(Base):
    """部门树 — 仅 id / parent_id / name，供各模块筛选"""

    __tablename__ = "meta_department"
    __table_args__ = (UniqueConstraint("parent_id", "name", name="uq_dept_parent_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("meta_department.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    parent: Mapped[Optional["MetaDepartment"]] = relationship(
        "MetaDepartment", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["MetaDepartment"]] = relationship(
        "MetaDepartment", back_populates="parent"
    )


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

