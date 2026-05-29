from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import MetaDepartment
from app.schemas import (
    DepartmentCreate,
    DepartmentFlat,
    DepartmentLazyNode,
    DepartmentNode,
    DepartmentUpdate,
    RootStatus,
)

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    dependencies=[Depends(get_current_user)],
)


def _validate_dept_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="部门名称不能为空")
    if "," in name or "，" in name:
        raise HTTPException(status_code=400, detail="部门名称不能包含逗号，批量添加请逐个创建")
    return name


def _validate_dept_code(code: str) -> str:
    code = code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="部门编码不能为空")
    if "," in code or "，" in code:
        raise HTTPException(status_code=400, detail="部门编码不能包含逗号")
    return code


def _build_tree(nodes: list[MetaDepartment]) -> list[DepartmentNode]:
    node_map: dict[str, DepartmentNode] = {}
    roots: list[DepartmentNode] = []

    for dept in nodes:
        node_map[dept.dept_code] = DepartmentNode(
            dept_code=dept.dept_code,
            parent_dept_code=dept.parent_dept_code,
            name=dept.name,
            children=[],
        )

    for dept in nodes:
        node = node_map[dept.dept_code]
        if dept.parent_dept_code is None:
            roots.append(node)
        elif dept.parent_dept_code in node_map:
            node_map[dept.parent_dept_code].children.append(node)

    roots.sort(key=lambda n: n.dept_code)
    for node in node_map.values():
        node.children.sort(key=lambda n: n.dept_code)

    return roots


def _get_or_404(db: Session, dept_code: str) -> MetaDepartment:
    dept = db.get(MetaDepartment, dept_code)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept


@router.get("/root-status", response_model=RootStatus)
def get_root_status(db: Session = Depends(get_db)):
    has_root = (
        db.query(MetaDepartment).filter(MetaDepartment.parent_dept_code.is_(None)).first() is not None
    )
    return RootStatus(has_root=has_root)


@router.get("/tree", response_model=list[DepartmentNode])
def get_department_tree(db: Session = Depends(get_db)):
    nodes = db.query(MetaDepartment).order_by(MetaDepartment.dept_code).all()
    return _build_tree(nodes)


@router.get("/children", response_model=list[DepartmentLazyNode])
def get_department_children(
    parent_dept_code: Optional[str] = Query(None, description="省略时返回根节点"),
    db: Session = Depends(get_db),
):
    if parent_dept_code is None:
        depts = (
            db.query(MetaDepartment)
            .filter(MetaDepartment.parent_dept_code.is_(None))
            .order_by(MetaDepartment.dept_code)
            .all()
        )
    else:
        depts = (
            db.query(MetaDepartment)
            .filter(MetaDepartment.parent_dept_code == parent_dept_code)
            .order_by(MetaDepartment.dept_code)
            .all()
        )

    if not depts:
        return []

    dept_codes = [dept.dept_code for dept in depts]
    child_rows = (
        db.query(MetaDepartment.parent_dept_code)
        .filter(MetaDepartment.parent_dept_code.in_(dept_codes))
        .distinct()
        .all()
    )
    parents_with_children = {row[0] for row in child_rows if row[0]}

    return [
        DepartmentLazyNode(
            dept_code=dept.dept_code,
            parent_dept_code=dept.parent_dept_code,
            name=dept.name,
            has_children=dept.dept_code in parents_with_children,
        )
        for dept in depts
    ]


@router.post("", response_model=DepartmentFlat, status_code=201, dependencies=[Depends(require_admin)])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    dept_code = _validate_dept_code(payload.dept_code)
    if db.get(MetaDepartment, dept_code):
        raise HTTPException(status_code=400, detail="部门编码已存在")

    if payload.parent_dept_code is None:
        if db.query(MetaDepartment).filter(MetaDepartment.parent_dept_code.is_(None)).first():
            raise HTTPException(status_code=400, detail="根节点已存在，请在根节点下添加子部门")
    else:
        parent_code = _validate_dept_code(payload.parent_dept_code)
        _get_or_404(db, parent_code)

    name = _validate_dept_name(payload.name)
    duplicate = (
        db.query(MetaDepartment)
        .filter(
            MetaDepartment.parent_dept_code == payload.parent_dept_code,
            MetaDepartment.name == name,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="同级下已存在同名部门")

    dept = MetaDepartment(
        dept_code=dept_code,
        parent_dept_code=payload.parent_dept_code,
        name=name,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_code}", response_model=DepartmentFlat, dependencies=[Depends(require_admin)])
def update_department(dept_code: str, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = _get_or_404(db, dept_code)
    name = _validate_dept_name(payload.name)

    duplicate = (
        db.query(MetaDepartment)
        .filter(
            MetaDepartment.parent_dept_code == dept.parent_dept_code,
            MetaDepartment.name == name,
            MetaDepartment.dept_code != dept_code,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="同级下已存在同名部门")

    dept.name = name
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_code}", status_code=204, dependencies=[Depends(require_admin)])
def delete_department(dept_code: str, db: Session = Depends(get_db)):
    dept = _get_or_404(db, dept_code)

    if db.query(MetaDepartment).filter(MetaDepartment.parent_dept_code == dept_code).count() > 0:
        raise HTTPException(status_code=400, detail="请先删除所有子部门")

    db.delete(dept)
    db.commit()
