from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import MetaDepartment, MetaFocusPdu
from app.schemas import FocusPduCreate, FocusPduItem, FocusPduListResponse
from app.services.dept_utils import get_dept_path
from app.services.focus_pdu import FOCUS_PDU_TREE_DEPTH, get_focus_pdu_depth, list_focus_pdu_rows

router = APIRouter(
    prefix="/focus-pdus",
    tags=["focus-pdus"],
    dependencies=[Depends(get_current_user)],
)


def _to_item(db: Session, row: MetaFocusPdu) -> FocusPduItem:
    path = get_dept_path(db, row.dept_code)
    dept = db.get(MetaDepartment, row.dept_code)
    return FocusPduItem(
        dept_code=row.dept_code,
        name=dept.name if dept else row.dept_code,
        alias=row.alias,
        sort_order=row.sort_order,
        path=path,
        depth=len(path),
    )


@router.get("/candidates", response_model=FocusPduListResponse)
def list_focus_pdu_candidates(db: Session = Depends(get_db)):
    """组织树中符合 PDU 层级的全部节点（用于管理端添加）"""
    focused = {row.dept_code for row in list_focus_pdu_rows(db)}
    items: list[FocusPduItem] = []
    for dept in db.query(MetaDepartment).order_by(MetaDepartment.dept_code).all():
        if dept.dept_code in focused:
            continue
        path = get_dept_path(db, dept.dept_code)
        if len(path) != FOCUS_PDU_TREE_DEPTH:
            continue
        items.append(
            FocusPduItem(
                dept_code=dept.dept_code,
                name=dept.name,
                alias=None,
                sort_order=0,
                path=path,
                depth=len(path),
            )
        )
    return FocusPduListResponse(items=items, target_depth=FOCUS_PDU_TREE_DEPTH)


@router.get("", response_model=FocusPduListResponse)
def list_focus_pdus(db: Session = Depends(get_db)):
    rows = list_focus_pdu_rows(db)
    return FocusPduListResponse(
        items=[_to_item(db, row) for row in rows],
        target_depth=FOCUS_PDU_TREE_DEPTH,
    )


@router.post("", response_model=FocusPduItem, dependencies=[Depends(require_admin)])
def add_focus_pdu(payload: FocusPduCreate, db: Session = Depends(get_db)):
    dept = db.get(MetaDepartment, payload.dept_code)
    if dept is None:
        raise HTTPException(status_code=404, detail="部门不存在")

    depth = get_focus_pdu_depth(db, payload.dept_code)
    if depth != FOCUS_PDU_TREE_DEPTH:
        raise HTTPException(
            status_code=400,
            detail=f"关注 PDU 须为组织树第 {FOCUS_PDU_TREE_DEPTH} 层节点（当前为第 {depth} 层）",
        )

    existing = db.get(MetaFocusPdu, payload.dept_code)
    if existing:
        if payload.alias is not None:
            existing.alias = payload.alias.strip() or None
        db.commit()
        db.refresh(existing)
        return _to_item(db, existing)

    max_order = db.query(MetaFocusPdu.sort_order).order_by(MetaFocusPdu.sort_order.desc()).limit(1).scalar()
    sort_order = (max_order or 0) + 1 if max_order is not None else 0
    row = MetaFocusPdu(
        dept_code=payload.dept_code,
        alias=(payload.alias.strip() if payload.alias else None),
        sort_order=sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_item(db, row)


@router.delete("/{dept_code}", status_code=204, dependencies=[Depends(require_admin)])
def remove_focus_pdu(dept_code: str, db: Session = Depends(get_db)):
    row = db.get(MetaFocusPdu, dept_code)
    if row is None:
        raise HTTPException(status_code=404, detail="未在关注列表中")
    db.delete(row)
    db.commit()
