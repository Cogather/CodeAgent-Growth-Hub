"""部门树工具函数"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import MetaDepartment

HR_DEPT_STORE_LEVELS = 6


def get_root(db: Session) -> MetaDepartment | None:
    return db.query(MetaDepartment).filter(MetaDepartment.parent_dept_code.is_(None)).first()


def get_dept_path(db: Session, dept_code: str) -> list[str]:
    """从根到当前节点的部门名称路径"""
    names: list[str] = []
    current = db.get(MetaDepartment, dept_code)
    while current:
        names.append(current.name)
        current = (
            db.get(MetaDepartment, current.parent_dept_code) if current.parent_dept_code else None
        )
    names.reverse()
    return names


def get_max_tree_depth(db: Session) -> int:
    max_depth = 0
    for dept in db.query(MetaDepartment).all():
        depth = len(get_dept_path(db, dept.dept_code))
        max_depth = max(max_depth, depth)
    return max_depth


def find_dept_by_path(db: Session, path_names: list[str]) -> MetaDepartment | None:
    """按名称路径在组织架构中查找节点，必须从根节点起完整匹配"""
    if not path_names:
        return None

    root = get_root(db)
    if not root or root.name != path_names[0]:
        return None

    current: MetaDepartment | None = root
    for name in path_names[1:]:
        if current is None:
            return None
        child = (
            db.query(MetaDepartment)
            .filter(MetaDepartment.parent_dept_code == current.dept_code, MetaDepartment.name == name)
            .first()
        )
        if not child:
            return None
        current = child
    return current


def hr_dept_visible_start() -> int:
    return get_settings().hr_org_start_level


def person_matches_dept_path(record: object, path_names: list[str]) -> bool:
    """部门树路径（自根起）与人员 dept_l3 起字段对齐匹配"""
    start = hr_dept_visible_start()
    for i, name in enumerate(path_names):
        dept_level = start + i
        if getattr(record, f"dept_l{dept_level}_name", None) != name:
            return False
    return True


def list_all_departments(db: Session) -> list[MetaDepartment]:
    return db.query(MetaDepartment).order_by(MetaDepartment.dept_code).all()
