from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import MetaDepartment
from app.schemas import DepartmentCreate, DepartmentFlat, DepartmentNode, DepartmentUpdate, RootStatus

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


def _build_tree(nodes: list[MetaDepartment]) -> list[DepartmentNode]:
    node_map: dict[int, DepartmentNode] = {}
    roots: list[DepartmentNode] = []

    for dept in nodes:
        node_map[dept.id] = DepartmentNode(id=dept.id, parent_id=dept.parent_id, name=dept.name, children=[])

    for dept in nodes:
        node = node_map[dept.id]
        if dept.parent_id is None:
            roots.append(node)
        elif dept.parent_id in node_map:
            node_map[dept.parent_id].children.append(node)

    roots.sort(key=lambda n: n.id)
    for node in node_map.values():
        node.children.sort(key=lambda n: n.id)

    return roots


def _get_or_404(db: Session, dept_id: int) -> MetaDepartment:
    dept = db.get(MetaDepartment, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept


@router.get("/root-status", response_model=RootStatus)
def get_root_status(db: Session = Depends(get_db)):
    has_root = db.query(MetaDepartment).filter(MetaDepartment.parent_id.is_(None)).first() is not None
    return RootStatus(has_root=has_root)


@router.get("/tree", response_model=list[DepartmentNode])
def get_department_tree(db: Session = Depends(get_db)):
    nodes = db.query(MetaDepartment).order_by(MetaDepartment.id).all()
    return _build_tree(nodes)


@router.post("", response_model=DepartmentFlat, status_code=201, dependencies=[Depends(require_admin)])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    if payload.parent_id is None:
        if db.query(MetaDepartment).filter(MetaDepartment.parent_id.is_(None)).first():
            raise HTTPException(status_code=400, detail="根节点已存在，请在根节点下添加子部门")
    else:
        _get_or_404(db, payload.parent_id)

    name = _validate_dept_name(payload.name)
    duplicate = (
        db.query(MetaDepartment)
        .filter(MetaDepartment.parent_id == payload.parent_id, MetaDepartment.name == name)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="同级下已存在同名部门")

    dept = MetaDepartment(parent_id=payload.parent_id, name=name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartmentFlat, dependencies=[Depends(require_admin)])
def update_department(dept_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = _get_or_404(db, dept_id)
    name = _validate_dept_name(payload.name)

    duplicate = (
        db.query(MetaDepartment)
        .filter(
            MetaDepartment.parent_id == dept.parent_id,
            MetaDepartment.name == name,
            MetaDepartment.id != dept_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="同级下已存在同名部门")

    dept.name = name
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    dept = _get_or_404(db, dept_id)

    if db.query(MetaDepartment).filter(MetaDepartment.parent_id == dept_id).count() > 0:
        raise HTTPException(status_code=400, detail="请先删除所有子部门")

    db.delete(dept)
    db.commit()
