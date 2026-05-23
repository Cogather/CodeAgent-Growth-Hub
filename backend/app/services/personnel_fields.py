"""人员部门层级字段工具"""

from __future__ import annotations

from app.models import DEPT_LEVELS, MetaPersonnel


def personnel_dept_names(person: MetaPersonnel) -> list[str]:
    names: list[str] = []
    for i in range(1, DEPT_LEVELS + 1):
        name = getattr(person, f"dept_l{i}_name")
        if name:
            names.append(name)
    return names


def apply_dept_fields_to_model(person: MetaPersonnel, fields: dict[str, str | None]) -> None:
    for key, value in fields.items():
        setattr(person, key, value)


def model_dept_fields_from_payload(payload: dict) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for i in range(1, DEPT_LEVELS + 1):
        name_key = f"dept_l{i}_name"
        code_key = f"dept_l{i}_code"
        result[name_key] = (payload.get(name_key) or "").strip() or None
        result[code_key] = (payload.get(code_key) or "").strip() or None
    return result
