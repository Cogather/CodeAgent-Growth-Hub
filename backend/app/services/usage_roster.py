"""使用统计 — 有权限人员名单（黄/蓝/绿区白名单并集）"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import MetaPersonnel, PermZoneBlue, PermZoneGreen, PermZoneYellow


def get_authorized_emp_nos(db: Session) -> set[str]:
    emp_nos: set[str] = set()
    for model_cls in (PermZoneYellow, PermZoneBlue, PermZoneGreen):
        for (emp_no,) in db.query(model_cls.emp_no).all():
            emp_nos.add(emp_no)
    return emp_nos


def list_authorized_personnel(db: Session) -> list[MetaPersonnel]:
    emp_nos = get_authorized_emp_nos(db)
    if not emp_nos:
        return []

    return (
        db.query(MetaPersonnel)
        .filter(MetaPersonnel.emp_no.in_(emp_nos))
        .order_by(MetaPersonnel.emp_no)
        .all()
    )
