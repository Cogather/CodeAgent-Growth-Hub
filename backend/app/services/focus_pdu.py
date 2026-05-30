"""重点关注 PDU（组织树固定层级节点）— 列表筛选与配置"""

from __future__ import annotations

from sqlalchemy import and_, or_
from sqlalchemy.orm import Query, Session

from app.models import MetaFocusPdu, MetaPersonnel
from app.services.dept_utils import get_dept_path

# 关注节点在组织树中的深度（根=1），与产品约定「三级 PDU」一致
FOCUS_PDU_TREE_DEPTH = 3


def get_focus_pdu_depth(db: Session, dept_code: str) -> int:
    return len(get_dept_path(db, dept_code))


def list_focus_pdu_rows(db: Session) -> list[MetaFocusPdu]:
    return db.query(MetaFocusPdu).order_by(MetaFocusPdu.sort_order, MetaFocusPdu.dept_code).all()


def personnel_path_clause(path_names: list[str]):
    """人员 dept_l1 起与组织树路径（自根）逐层对齐"""
    if not path_names:
        return None
    parts = []
    for i, name in enumerate(path_names[:7], start=1):
        column = getattr(MetaPersonnel, f"dept_l{i}_name")
        parts.append(column == name)
    return and_(*parts)


def apply_focus_pdu_scope(query: Query, db: Session, *, enabled: bool) -> Query:
    """开启时仅保留落在任一关注 PDU 子树内的人员（路径前缀匹配）"""
    if not enabled:
        return query

    rows = list_focus_pdu_rows(db)
    if not rows:
        return query.filter(MetaPersonnel.emp_no == "__no_focus_pdu__")

    clauses = []
    for row in rows:
        path = get_dept_path(db, row.dept_code)
        clause = personnel_path_clause(path)
        if clause is not None:
            clauses.append(clause)

    if not clauses:
        return query.filter(MetaPersonnel.emp_no == "__no_focus_pdu__")

    return query.filter(or_(*clauses))
