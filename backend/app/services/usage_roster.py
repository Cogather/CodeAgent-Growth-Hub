"""使用统计 — 有权限人员名单（黄区 + 绿区白名单并集；蓝区单独统计暂不纳入）"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import MetaPersonnel, PermZoneGreen, PermZoneYellow

USAGE_ROSTER_ZONE_MODELS = (PermZoneYellow, PermZoneGreen)


def get_usage_roster_emp_nos(db: Session) -> set[str]:
    emp_nos: set[str] = set()
    for model_cls in USAGE_ROSTER_ZONE_MODELS:
        for (emp_no,) in db.query(model_cls.emp_no).all():
            emp_nos.add(emp_no)
    return emp_nos


def list_usage_roster_personnel(db: Session) -> list[MetaPersonnel]:
    emp_nos = get_usage_roster_emp_nos(db)
    if not emp_nos:
        return []

    return (
        db.query(MetaPersonnel)
        .filter(MetaPersonnel.emp_no.in_(emp_nos))
        .order_by(MetaPersonnel.emp_no)
        .all()
    )


# 兼容旧调用名
def list_authorized_personnel(db: Session) -> list[MetaPersonnel]:
    return list_usage_roster_personnel(db)


def get_authorized_emp_nos(db: Session) -> set[str]:
    return get_usage_roster_emp_nos(db)
