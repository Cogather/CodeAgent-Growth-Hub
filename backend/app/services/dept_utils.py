"""部门树工具函数"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import MetaDepartment


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


def person_matches_dept_path(record: object, path_names: list[str]) -> bool:
    """记录的一级至 N 级部门名称是否与给定路径完全匹配"""
    for i, name in enumerate(path_names, start=1):
        if getattr(record, f"dept_l{i}_name", None) != name:
            return False
    return True


def list_all_departments(db: Session) -> list[MetaDepartment]:
    return db.query(MetaDepartment).order_by(MetaDepartment.dept_code).all()
