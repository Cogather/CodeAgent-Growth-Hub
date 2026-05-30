import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import MetaPersonnel
from app.schemas import (
    ZoneImportFailureItem,
    ZonePermissionBatchRequest,
    ZonePermissionBatchResponse,
    ZonePermissionItem,
    ZonePermissionListResponse,
    ZonePermissionUpdate,
)
from app.services.hr_lookup import display_emp_no
from app.services.zone_config import ZONES, get_zone

router = APIRouter(
    prefix="/zone-permissions",
    tags=["zone-permissions"],
    dependencies=[Depends(get_current_user)],
)


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


@router.get("/zones")
def list_zones():
    return [{"key": z.key, "label": z.label, "model_hint": z.model_hint} for z in ZONES.values()]


@router.get("/{zone}", response_model=ZonePermissionListResponse)
def list_zone_permissions(zone: str, db: Session = Depends(get_db)):
    try:
        cfg = get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    model_cls = cfg.model_class
    rows = (
        db.query(model_cls, MetaPersonnel)
        .join(MetaPersonnel, model_cls.emp_no == MetaPersonnel.emp_no)
        .order_by(model_cls.emp_no)
        .all()
    )
    items: list[ZonePermissionItem] = []

    for row, person in rows:
        items.append(
            ZonePermissionItem(
                emp_no=row.emp_no,
                display_emp_no=display_emp_no(person.name, person.emp_no),
                name=person.name,
                models=_models_from_str(row.models),
            )
        )

    return ZonePermissionListResponse(zone=cfg.key, zone_label=cfg.label, items=items)


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
        get_zone(zone)
    except KeyError:
        raise HTTPException(status_code=404, detail="未知网络区域")

    model_cls = get_zone(zone).model_class
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

    return ZonePermissionItem(
        emp_no=row.emp_no,
        display_emp_no=display_emp_no(person.name, person.emp_no),
        name=person.name,
        models=models,
    )


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
