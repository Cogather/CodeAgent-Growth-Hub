"""人员批量导入：逐条查 HR、校验、写入；支持分批 commit 避免长事务"""

from __future__ import annotations

import re

from typing import Optional

from sqlalchemy.orm import Session

from app.models import MetaPersonnel
from app.schemas import ImportFailureItem, PersonnelBatchImportResponse
from app.services.dept_utils import HR_DEPT_STORE_LEVELS, get_root, hr_dept_visible_start
from app.services.hr_lookup import (
    count_org_dept_levels,
    lookup_employee,
    name_to_initial,
    org_dept_names_from_employee,
    personnel_fields_from_employee,
)

COMMIT_BATCH_SIZE = 20


def parse_emp_nos(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for part in re.split(r"[,，\s]+", text):
        emp_no = part.strip()
        if emp_no and emp_no not in seen:
            seen.add(emp_no)
            result.append(emp_no)
    return result


def _validate_against_org_root(db: Session, hr_dept_names: list[str]) -> Optional[str]:
    root = get_root(db)
    if not root:
        return None
    if not hr_dept_names:
        return "HR 未返回部门信息"
    if hr_dept_names[0] != root.name:
        return f"一级部门「{hr_dept_names[0]}」与组织架构根节点「{root.name}」不一致"
    return None


def import_personnel_batch(db: Session, emp_nos: list[str]) -> PersonnelBatchImportResponse:
    imported_count = 0
    pending_since_commit = 0
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
        pending_since_commit += 1

        if pending_since_commit >= COMMIT_BATCH_SIZE:
            db.commit()
            pending_since_commit = 0

    if pending_since_commit:
        db.commit()

    return PersonnelBatchImportResponse(imported_count=imported_count, failures=failures)
