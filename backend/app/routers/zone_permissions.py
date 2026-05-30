import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import DEPT_LEVELS, MetaPersonnel
from app.schemas import (
    PersonnelDistinctResponse,
    ZoneEmpNosResponse,
    ZoneExportFailuresRequest,
    ZoneImportFailureItem,
    ZonePermissionBatchRequest,
    ZonePermissionBatchResponse,
    ZonePermissionItem,
    ZonePermissionListResponse,
    ZonePermissionUpdate,
)
from app.services.excel_export import build_zone_import_exceptions_excel
from app.services.hr_lookup import display_emp_no
from app.services.zone_config import ZONES, get_zone

router = APIRouter(
    prefix="/zone-permissions",
    tags=["zone-permissions"],
    dependencies=[Depends(get_current_user)],
)

ZONE_DISTINCT_FIELDS = frozenset({f"dept_l{i}_name" for i in range(3, DEPT_LEVELS + 1)})


def _parse_csv(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for part in re.split(r"[,，\s]+", text):
        item = part.strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _models_to_str(models: list[str]) -> str:
    return ",".join(models)


def _models_from_str(raw: str) -> list[str]:
    return _parse_csv(raw)


def _apply_dept_name_filter(query, level: int, value: Optional[str]):
    if value is None:
        return query
    column = getattr(MetaPersonnel, f"dept_l{level}_name")
    if value == "":
        return query.filter(or_(column.is_(None), column == ""))
    return query.filter(column == value)


def _to_zone_item(row, person: MetaPersonnel) -> ZonePermissionItem:
    fields = {f"dept_l{i}_name": getattr(person, f"dept_l{i}_name") for i in range(1, DEPT_LEVELS + 1)}
    fields.update({f"dept_l{i}_code": getattr(person, f"dept_l{i}_code") for i in range(1, DEPT_LEVELS + 1)})
    return ZonePermissionItem(
        emp_no=row.emp_no,
        display_emp_no=display_emp_no(person.name, person.emp_no),
        name=person.name,
        models=_models_from_str(row.models),
        **fields,
    )


def _zone_joined_query(db: Session, model_cls):
    return db.query(model_cls, MetaPersonnel).join(
        MetaPersonnel, model_cls.emp_no == MetaPersonnel.emp_no
    )


@router.get("/zones")
def list_zones():
    return [{"key": z.key, "label": z.label, "model_hint": z.model_hint} for z in ZONES.values()]


@router.get("/{zone}/emp-nos", response_model=ZoneEmpNosResponse)
def list_zone_emp_nos(zone: str, db: Session = Depends(get_db)):
    try:
        model_cls = get_zone(zone).model_class
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    rows = db.query(model_cls.emp_no).order_by(model_cls.emp_no).all()
    return ZoneEmpNosResponse(emp_nos=[row[0] for row in rows])


@router.get("/{zone}/distinct/{field}", response_model=PersonnelDistinctResponse)
def zone_distinct_values(
    zone: str,
    field: str,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    try:
        model_cls = get_zone(zone).model_class
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    if field not in ZONE_DISTINCT_FIELDS:
        raise HTTPException(status_code=400, detail="不支持的筛选项")

    column = getattr(MetaPersonnel, field)
    rows = (
        db.query(column)
        .join(model_cls, model_cls.emp_no == MetaPersonnel.emp_no)
        .distinct()
        .order_by(column)
        .limit(limit)
        .all()
    )
    values = [row[0] if row[0] is not None else "" for row in rows]
    return PersonnelDistinctResponse(values=values)


@router.get("/{zone}", response_model=ZonePermissionListResponse)
def list_zone_permissions(
    zone: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None, description="工号或姓名模糊搜索"),
    dept_l3_name: Optional[str] = Query(None),
    dept_l4_name: Optional[str] = Query(None),
    dept_l5_name: Optional[str] = Query(None),
    dept_l6_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        cfg = get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    model_cls = cfg.model_class
    base_query = _zone_joined_query(db, model_cls)
    total_all = base_query.count()

    query = base_query
    if q:
        keyword = f"%{q.strip()}%"
        query = query.filter(
            or_(MetaPersonnel.emp_no.like(keyword), MetaPersonnel.name.like(keyword))
        )

    for level, value in {3: dept_l3_name, 4: dept_l4_name, 5: dept_l5_name, 6: dept_l6_name}.items():
        query = _apply_dept_name_filter(query, level, value)

    total = query.count()
    rows = (
        query.order_by(model_cls.emp_no)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ZonePermissionListResponse(
        zone=cfg.key,
        zone_label=cfg.label,
        items=[_to_zone_item(row, person) for row, person in rows],
        total=total,
        total_all=total_all,
        page=page,
        page_size=page_size,
    )


@router.post("/{zone}/export-exceptions", dependencies=[Depends(require_admin)])
def export_zone_import_exceptions(zone: str, payload: ZoneExportFailuresRequest):
    try:
        get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    if not payload.failures:
        raise HTTPException(status_code=400, detail="没有异常记录可导出")

    data = build_zone_import_exceptions_excel([f.model_dump() for f in payload.failures])
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="zone_{zone}_import_exceptions.xlsx"'},
    )


@router.post("/{zone}/batch", response_model=ZonePermissionBatchResponse, dependencies=[Depends(require_admin)])
def batch_upsert_zone_permissions(
    zone: str, payload: ZonePermissionBatchRequest, db: Session = Depends(get_db)
):
    try:
        cfg = get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    emp_nos = _parse_csv(payload.emp_nos_text)
    models = _parse_csv(payload.models_text)

    if not emp_nos:
        raise HTTPException(status_code=400, detail="请输入至少一个工号")
    if not models:
        raise HTTPException(status_code=400, detail="请输入至少一个模型")

    model_cls = cfg.model_class
    models_str = _models_to_str(models)
    upserted_count = 0
    failures: list[ZoneImportFailureItem] = []

    personnel_set = {
        row[0]
        for row in db.query(MetaPersonnel.emp_no).filter(MetaPersonnel.emp_no.in_(emp_nos)).all()
    }
    existing_map = {
        row.emp_no: row
        for row in db.query(model_cls).filter(model_cls.emp_no.in_(emp_nos)).all()
    }

    for emp_no in emp_nos:
        if emp_no not in personnel_set:
            failures.append(
                ZoneImportFailureItem(emp_no=emp_no, reason="工号不在全员名单中，请先录入人员")
            )
            continue

        existing = existing_map.get(emp_no)
        if existing:
            existing.models = models_str
        else:
            new_row = model_cls(emp_no=emp_no, models=models_str)
            db.add(new_row)
            existing_map[emp_no] = new_row
        upserted_count += 1

    if upserted_count:
        db.commit()

    return ZonePermissionBatchResponse(upserted_count=upserted_count, failures=failures)


@router.put("/{zone}/{emp_no}", response_model=ZonePermissionItem, dependencies=[Depends(require_admin)])
def update_zone_permission(
    zone: str, emp_no: str, payload: ZonePermissionUpdate, db: Session = Depends(get_db)
):
    try:
        cfg = get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    model_cls = cfg.model_class
    row = db.get(model_cls, emp_no)
    if not row:
        raise HTTPException(status_code=404, detail="该人员不在本区白名单中")

    models = _parse_csv(payload.models_text)
    if not models:
        raise HTTPException(status_code=400, detail="请输入至少一个模型")

    person = db.get(MetaPersonnel, emp_no)
    if not person:
        raise HTTPException(status_code=400, detail="工号不在全员名单中")

    row.models = _models_to_str(models)
    db.commit()
    db.refresh(row)

    return _to_zone_item(row, person)


@router.delete("/{zone}/{emp_no}", status_code=204, dependencies=[Depends(require_admin)])
def delete_zone_permission(zone: str, emp_no: str, db: Session = Depends(get_db)):
    try:
        cfg = get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    row = db.get(cfg.model_class, emp_no)
    if not row:
        raise HTTPException(status_code=404, detail="该人员不在本区白名单中")
    db.delete(row)
    db.commit()
