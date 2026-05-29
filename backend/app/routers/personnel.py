from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import DEPT_LEVELS, MetaPersonnel
from app.schemas import (
    ExportExceptionsRequest,
    PersonnelBatchImportRequest,
    PersonnelBatchImportResponse,
    PersonnelDistinctResponse,
    PersonnelItem,
    PersonnelListResponse,
    PersonnelUpdate,
)
from app.services.excel_export import build_import_exceptions_excel
from app.services.hr_lookup import display_emp_no, name_to_initial
from app.services.personnel_fields import apply_dept_fields_to_model, model_dept_fields_from_payload
from app.services.personnel_import import import_personnel_batch, parse_emp_nos

router = APIRouter(
    prefix="/personnel",
    tags=["personnel"],
    dependencies=[Depends(get_current_user)],
)

PERSONNEL_DISTINCT_FIELDS = frozenset(
    {f"dept_l{i}_name" for i in range(3, DEPT_LEVELS + 1)}
)


def _to_personnel_item(p: MetaPersonnel) -> PersonnelItem:
    fields = {f"dept_l{i}_name": getattr(p, f"dept_l{i}_name") for i in range(1, DEPT_LEVELS + 1)}
    fields.update({f"dept_l{i}_code": getattr(p, f"dept_l{i}_code") for i in range(1, DEPT_LEVELS + 1)})
    return PersonnelItem(
        emp_no=p.emp_no,
        display_emp_no=display_emp_no(p.name, p.emp_no),
        name=p.name,
        **fields,
    )


def _apply_dept_name_filter(query, level: int, value: Optional[str]):
    if value is None:
        return query
    column = getattr(MetaPersonnel, f"dept_l{level}_name")
    if value == "":
        return query.filter(or_(column.is_(None), column == ""))
    return query.filter(column == value)


@router.get("", response_model=PersonnelListResponse)
def list_personnel(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None, description="工号或姓名模糊搜索"),
    dept_l3_name: Optional[str] = Query(None),
    dept_l4_name: Optional[str] = Query(None),
    dept_l5_name: Optional[str] = Query(None),
    dept_l6_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(MetaPersonnel)

    if q:
        keyword = f"%{q.strip()}%"
        query = query.filter(
            or_(MetaPersonnel.emp_no.like(keyword), MetaPersonnel.name.like(keyword))
        )

    dept_filters = {
        3: dept_l3_name,
        4: dept_l4_name,
        5: dept_l5_name,
        6: dept_l6_name,
    }
    for level, value in dept_filters.items():
        query = _apply_dept_name_filter(query, level, value)

    total = query.count()
    personnel = (
        query.order_by(MetaPersonnel.emp_no)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PersonnelListResponse(
        items=[_to_personnel_item(p) for p in personnel],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/distinct/{field}", response_model=PersonnelDistinctResponse)
def personnel_distinct_values(
    field: str,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if field not in PERSONNEL_DISTINCT_FIELDS:
        raise HTTPException(status_code=400, detail="不支持的筛选项")

    column = getattr(MetaPersonnel, field)
    rows = (
        db.query(column)
        .distinct()
        .order_by(column)
        .limit(limit)
        .all()
    )
    values = [row[0] if row[0] is not None else "" for row in rows]
    return PersonnelDistinctResponse(values=values)


@router.post("/batch-import", response_model=PersonnelBatchImportResponse, dependencies=[Depends(require_admin)])
def batch_import_personnel(payload: PersonnelBatchImportRequest, db: Session = Depends(get_db)):
    emp_nos = parse_emp_nos(payload.emp_nos_text)
    if not emp_nos:
        raise HTTPException(status_code=400, detail="请输入至少一个工号")

    return import_personnel_batch(db, emp_nos)


@router.post("/export-exceptions", dependencies=[Depends(require_admin)])
def export_import_exceptions(payload: ExportExceptionsRequest):
    if not payload.failures:
        raise HTTPException(status_code=400, detail="没有异常记录可导出")

    data = build_import_exceptions_excel([f.model_dump() for f in payload.failures])
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="personnel_import_exceptions.xlsx"'},
    )


@router.put("/{emp_no}", response_model=PersonnelItem, dependencies=[Depends(require_admin)])
def update_personnel(emp_no: str, payload: PersonnelUpdate, db: Session = Depends(get_db)):
    person = db.get(MetaPersonnel, emp_no)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    person.name = payload.name.strip()
    person.name_initial = name_to_initial(person.name)
    dept_fields = model_dept_fields_from_payload(payload.model_dump())
    apply_dept_fields_to_model(person, dept_fields)
    db.commit()
    db.refresh(person)
    return _to_personnel_item(person)


@router.delete("/{emp_no}", status_code=204, dependencies=[Depends(require_admin)])
def delete_personnel(emp_no: str, db: Session = Depends(get_db)):
    person = db.get(MetaPersonnel, emp_no)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    db.delete(person)
    db.commit()
