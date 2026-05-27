from __future__ import annotations

import re

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import DEPT_LEVELS, MetaPersonnel
from app.schemas import (
    ExportExceptionsRequest,
    ImportFailureItem,
    PersonnelBatchImportRequest,
    PersonnelBatchImportResponse,
    PersonnelItem,
    PersonnelListResponse,
    PersonnelUpdate,
)
from app.services.dept_utils import HR_DEPT_STORE_LEVELS, get_root, hr_dept_visible_start
from app.services.excel_export import build_import_exceptions_excel
from app.services.hr_lookup import (
    count_org_dept_levels,
    display_emp_no,
    lookup_employee,
    name_to_initial,
    org_dept_names_from_employee,
    personnel_fields_from_employee,
)
from app.services.personnel_fields import apply_dept_fields_to_model, model_dept_fields_from_payload

router = APIRouter(
    prefix="/personnel",
    tags=["personnel"],
    dependencies=[Depends(get_current_user)],
)


def _parse_emp_nos(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for part in re.split(r"[,，\s]+", text):
        emp_no = part.strip()
        if emp_no and emp_no not in seen:
            seen.add(emp_no)
            result.append(emp_no)
    return result


def _to_personnel_item(p: MetaPersonnel) -> PersonnelItem:
    fields = {f"dept_l{i}_name": getattr(p, f"dept_l{i}_name") for i in range(1, DEPT_LEVELS + 1)}
    fields.update({f"dept_l{i}_code": getattr(p, f"dept_l{i}_code") for i in range(1, DEPT_LEVELS + 1)})
    return PersonnelItem(
        emp_no=p.emp_no,
        display_emp_no=display_emp_no(p.name, p.emp_no),
        name=p.name,
        **fields,
    )


def _validate_against_org_root(db: Session, hr_dept_names: list[str]) -> Optional[str]:
    """一级部门须与组织架构根节点一致（若已配置根节点）"""
    root = get_root(db)
    if not root:
        return None
    if not hr_dept_names:
        return "HR 未返回部门信息"
    if hr_dept_names[0] != root.name:
        return f"一级部门「{hr_dept_names[0]}」与组织架构根节点「{root.name}」不一致"
    return None


@router.get("", response_model=PersonnelListResponse)
def list_personnel(db: Session = Depends(get_db)):
    personnel = db.query(MetaPersonnel).order_by(MetaPersonnel.emp_no).all()
    return PersonnelListResponse(items=[_to_personnel_item(p) for p in personnel])


@router.post("/batch-import", response_model=PersonnelBatchImportResponse, dependencies=[Depends(require_admin)])
def batch_import_personnel(payload: PersonnelBatchImportRequest, db: Session = Depends(get_db)):
    emp_nos = _parse_emp_nos(payload.emp_nos_text)
    if not emp_nos:
        raise HTTPException(status_code=400, detail="请输入至少一个工号")

    imported_count = 0
    failures: list[ImportFailureItem] = []
    seen_accounts: set[str] = set()

    for query_emp_no in emp_nos:
        hr = lookup_employee(query_emp_no)
        if not hr:
            failures.append(ImportFailureItem(emp_no=query_emp_no, reason="HR 未返回该工号信息"))
            continue

        store_emp_no = hr.emp_no
        if store_emp_no in seen_accounts:
            failures.append(
                ImportFailureItem(
                    emp_no=query_emp_no,
                    name=hr.name,
                    reason=f"本批重复（账号 {store_emp_no}）",
                )
            )
            continue
        seen_accounts.add(store_emp_no)

        dept_names = org_dept_names_from_employee(hr)
        org_level_count = count_org_dept_levels(hr.raw) if hr.raw else len(dept_names)
        max_org_levels = HR_DEPT_STORE_LEVELS - hr_dept_visible_start() + 1
        if org_level_count > max_org_levels:
            failures.append(
                ImportFailureItem(
                    emp_no=query_emp_no,
                    name=hr.name,
                    hr_dept_path=dept_names,
                    reason=f"组织可见部门超过 {max_org_levels} 级，无法录入",
                )
            )
            continue

        if not dept_names:
            failures.append(
                ImportFailureItem(
                    emp_no=query_emp_no,
                    name=hr.name,
                    reason="HR 未返回可对齐组织架构的部门信息",
                )
            )
            continue

        root_err = _validate_against_org_root(db, dept_names)
        if root_err:
            failures.append(
                ImportFailureItem(
                    emp_no=query_emp_no,
                    name=hr.name,
                    hr_dept_path=dept_names,
                    reason=root_err,
                )
            )
            continue

        if db.get(MetaPersonnel, store_emp_no):
            failures.append(
                ImportFailureItem(
                    emp_no=query_emp_no,
                    name=hr.name,
                    hr_dept_path=dept_names,
                    reason=f"该账号已在人员名单中（{store_emp_no}）",
                )
            )
            continue

        dept_fields = personnel_fields_from_employee(hr)
        db.add(
            MetaPersonnel(
                emp_no=store_emp_no,
                name=hr.name,
                name_initial=name_to_initial(hr.name),
                **dept_fields,
            )
        )
        imported_count += 1

    if imported_count:
        db.commit()

    return PersonnelBatchImportResponse(imported_count=imported_count, failures=failures)


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
