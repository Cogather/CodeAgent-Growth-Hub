from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.auth import get_current_user, require_admin
from app.models import DEPT_LEVELS, MetaPersonnel, StatUsage
from app.schemas import (
    PersonnelDistinctResponse,
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
    ParsedUsageRow,
    build_usage_import_failures_excel,
    build_usage_template_excel,
    build_zero_usage_excel,
    parse_usage_excel,
)
from app.services.usage_roster import get_usage_roster_emp_nos

router = APIRouter(
    prefix="/usage-stats",
    tags=["usage-stats"],
    dependencies=[Depends(get_current_user)],
)

USAGE_DISTINCT_FIELDS = frozenset({f"dept_l{i}_name" for i in range(3, DEPT_LEVELS + 1)})


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


def _apply_dept_name_filter(query, level: int, value: Optional[str]):
    if value is None:
        return query
    column = getattr(MetaPersonnel, f"dept_l{level}_name")
    if value == "":
        return query.filter(or_(column.is_(None), column == ""))
    return query.filter(column == value)


def _roster_personnel_query(db: Session):
    emp_nos = get_usage_roster_emp_nos(db)
    if not emp_nos:
        return None
    return (
        db.query(MetaPersonnel, StatUsage.usage_count)
        .outerjoin(StatUsage, MetaPersonnel.emp_no == StatUsage.emp_no)
        .filter(MetaPersonnel.emp_no.in_(emp_nos))
    )


def _to_usage_item(person: MetaPersonnel, usage_count: int | None) -> UsageStatItem:
    return UsageStatItem(
        emp_no=person.emp_no,
        display_emp_no=display_emp_no(person.name, person.emp_no),
        name=person.name,
        usage_count=int(usage_count or 0),
        **_personnel_dept_fields(person),
    )


def _build_merged_items(db: Session) -> list[UsageStatItem]:
    """全量合并列表（导出零使用人员等场景）"""
    query = _roster_personnel_query(db)
    if query is None:
        return []

    rows = query.order_by(
        func.coalesce(StatUsage.usage_count, 0).desc(),
        MetaPersonnel.emp_no,
    ).all()
    return [_to_usage_item(person, usage_count) for person, usage_count in rows]


@router.get("/distinct/{field}", response_model=PersonnelDistinctResponse)
def usage_distinct_values(
    field: str,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if field not in USAGE_DISTINCT_FIELDS:
        raise HTTPException(status_code=400, detail="不支持的筛选项")

    emp_nos = get_usage_roster_emp_nos(db)
    if not emp_nos:
        return PersonnelDistinctResponse(values=[])

    column = getattr(MetaPersonnel, field)
    rows = (
        db.query(column)
        .filter(MetaPersonnel.emp_no.in_(emp_nos))
        .distinct()
        .order_by(column)
        .limit(limit)
        .all()
    )
    values = [row[0] if row[0] is not None else "" for row in rows]
    return PersonnelDistinctResponse(values=values)


@router.get("", response_model=UsageStatListResponse)
def list_usage_stats(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None, description="工号或姓名模糊搜索"),
    dept_l3_name: Optional[str] = Query(None),
    dept_l4_name: Optional[str] = Query(None),
    dept_l5_name: Optional[str] = Query(None),
    dept_l6_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    base_query = _roster_personnel_query(db)
    if base_query is None:
        return UsageStatListResponse(
            items=[],
            total=0,
            total_all=0,
            page=page,
            page_size=page_size,
            imported_at=_last_imported_at(db),
        )

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
        query.order_by(
            func.coalesce(StatUsage.usage_count, 0).desc(),
            MetaPersonnel.emp_no,
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return UsageStatListResponse(
        items=[_to_usage_item(person, usage_count) for person, usage_count in rows],
        total=total,
        total_all=total_all,
        page=page,
        page_size=page_size,
        imported_at=_last_imported_at(db),
    )


@router.get("/template")
def download_usage_template():
    data = build_usage_template_excel()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="usage_stats_template.xlsx"'},
    )


@router.post("/import", response_model=UsageStatImportResponse, dependencies=[Depends(require_admin)])
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

    roster_emp_nos = get_usage_roster_emp_nos(db)
    valid_rows: list[StatUsage] = []
    not_on_roster: list[ParsedUsageRow] = []

    for row in parsed.rows:
        if row.emp_no not in roster_emp_nos:
            not_on_roster.append(row)
            continue
        valid_rows.append(StatUsage(emp_no=row.emp_no, usage_count=row.usage_count))

    if not_on_roster:
        missing_emp_nos = [row.emp_no for row in not_on_roster]
        existing_emp_nos = {
            emp_no
            for (emp_no,) in db.query(MetaPersonnel.emp_no)
            .filter(MetaPersonnel.emp_no.in_(missing_emp_nos))
            .all()
        }
        for row in not_on_roster:
            if row.emp_no not in existing_emp_nos:
                reason = "工号不在全员名单中"
            else:
                reason = "工号未配置黄区或绿区权限"
            failures.append(
                UsageImportFailureItem(emp_no=row.emp_no, usage_count=row.usage_count, reason=reason)
            )

    if not valid_rows:
        if not parsed.rows and not failures:
            raise HTTPException(status_code=400, detail="Excel 中没有可导入的数据行")
        return UsageStatImportResponse(imported_count=0, failures=failures)

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.query(StatUsage).delete()
    mappings = [
        {"emp_no": row.emp_no, "usage_count": row.usage_count, "imported_at": now} for row in valid_rows
    ]
    db.bulk_insert_mappings(StatUsage, mappings)
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
