from __future__ import annotations

from sqlalchemy import func

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DEPT_LEVELS, MetaPersonnel, StatUsage
from app.schemas import (
    UsageExportExceptionsRequest,
    UsageExportZeroUsageRequest,
    UsageImportFailureItem,
    UsageStatImportResponse,
    UsageStatItem,
    UsageStatListResponse,
)
from app.services.dept_utils import person_matches_dept_path
from app.services.hr_lookup import display_emp_no
from app.services.usage_excel import (
    build_usage_import_failures_excel,
    build_usage_template_excel,
    build_zero_usage_excel,
    parse_usage_excel,
)
from app.services.usage_roster import list_authorized_personnel

router = APIRouter(prefix="/usage-stats", tags=["usage-stats"])


def _last_imported_at(db: Session) -> str | None:
    ts = db.query(func.max(StatUsage.imported_at)).scalar()
    if ts is None:
        return None
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _personnel_dept_fields(person: MetaPersonnel) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for i in range(1, DEPT_LEVELS + 1):
        fields[f"dept_l{i}_name"] = getattr(person, f"dept_l{i}_name")
        fields[f"dept_l{i}_code"] = getattr(person, f"dept_l{i}_code")
    return fields


def _build_merged_items(db: Session) -> list[UsageStatItem]:
    personnel = list_authorized_personnel(db)
    if not personnel:
        return []

    emp_nos = [p.emp_no for p in personnel]
    usage_map = {
        row.emp_no: row.usage_count
        for row in db.query(StatUsage).filter(StatUsage.emp_no.in_(emp_nos)).all()
    }

    items: list[UsageStatItem] = []
    for person in personnel:
        items.append(
            UsageStatItem(
                emp_no=person.emp_no,
                display_emp_no=display_emp_no(person.name, person.emp_no),
                name=person.name,
                usage_count=usage_map.get(person.emp_no, 0),
                **_personnel_dept_fields(person),
            )
        )
    return items


@router.get("", response_model=UsageStatListResponse)
def list_usage_stats(db: Session = Depends(get_db)):
    return UsageStatListResponse(items=_build_merged_items(db), imported_at=_last_imported_at(db))


@router.get("/template")
def download_usage_template():
    data = build_usage_template_excel()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="usage_stats_template.xlsx"'},
    )


@router.post("/import", response_model=UsageStatImportResponse)
async def import_usage_stats(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 格式的 Excel 文件")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")

    try:
        parsed = parse_usage_excel(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    failures: list[UsageImportFailureItem] = [
        UsageImportFailureItem(
            emp_no=item.get("emp_no", ""),
            usage_count=item.get("usage_count"),
            reason=item.get("reason", ""),
        )
        for item in parsed.failures
    ]

    authorized = {p.emp_no for p in list_authorized_personnel(db)}
    valid_rows: list[StatUsage] = []

    for row in parsed.rows:
        if row.emp_no not in authorized:
            person = db.get(MetaPersonnel, row.emp_no)
            if person is None:
                reason = "工号不在全员名单中"
            else:
                reason = "工号未配置任何网络区域权限（黄/蓝/绿区）"
            failures.append(
                UsageImportFailureItem(emp_no=row.emp_no, usage_count=row.usage_count, reason=reason)
            )
            continue
        valid_rows.append(StatUsage(emp_no=row.emp_no, usage_count=row.usage_count))

    if not valid_rows:
        if not parsed.rows and not failures:
            raise HTTPException(status_code=400, detail="Excel 中没有可导入的数据行")
        return UsageStatImportResponse(imported_count=0, failures=failures)

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.query(StatUsage).delete()
    for row in valid_rows:
        row.imported_at = now
        db.add(row)
    db.commit()

    return UsageStatImportResponse(imported_count=len(valid_rows), failures=failures)


@router.post("/export-exceptions")
def export_usage_import_exceptions(payload: UsageExportExceptionsRequest):
    if not payload.failures:
        raise HTTPException(status_code=400, detail="没有异常记录可导出")

    data = build_usage_import_failures_excel([f.model_dump() for f in payload.failures])
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="usage_import_exceptions.xlsx"'},
    )


@router.post("/export-zero-usage")
def export_zero_usage_personnel(payload: UsageExportZeroUsageRequest, db: Session = Depends(get_db)):
    items = _build_merged_items(db)
    zero_items = [item for item in items if item.usage_count == 0]

    if payload.dept_path:
        zero_items = [item for item in zero_items if person_matches_dept_path(item, payload.dept_path)]

    if not zero_items:
        raise HTTPException(status_code=400, detail="当前范围内没有使用次数为 0 的人员")

    data = build_zero_usage_excel([item.model_dump() for item in zero_items])
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="usage_zero_users.xlsx"'},
    )
