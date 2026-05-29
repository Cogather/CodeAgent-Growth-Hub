from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import DEPT_LEVELS, MetaPersonnel
from app.schemas import (
    ExportExceptionsRequest,
    PersonnelBatchImportRequest,
    PersonnelBatchImportResponse,
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


def _to_personnel_item(p: MetaPersonnel) -> PersonnelItem:
    fields = {f"dept_l{i}_name": getattr(p, f"dept_l{i}_name") for i in range(1, DEPT_LEVELS + 1)}
    fields.update({f"dept_l{i}_code": getattr(p, f"dept_l{i}_code") for i in range(1, DEPT_LEVELS + 1)})
    return PersonnelItem(
        emp_no=p.emp_no,
        display_emp_no=display_emp_no(p.name, p.emp_no),
        name=p.name,
        **fields,
    )


@router.get("", response_model=PersonnelListResponse)
def list_personnel(db: Session = Depends(get_db)):
    personnel = db.query(MetaPersonnel).order_by(MetaPersonnel.emp_no).all()
    return PersonnelListResponse(items=[_to_personnel_item(p) for p in personnel])


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
