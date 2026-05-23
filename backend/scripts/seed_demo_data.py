#!/usr/bin/env python3
"""插入演示用人员与权限数据，便于查看权限统计饼图。cd backend && .venv/bin/python scripts/seed_demo_data.py"""

from __future__ import annotations

from app.database import SessionLocal
from app.models import MetaDepartment, MetaPersonnel, PermZoneBlue, PermZoneGreen, PermZoneYellow
from app.services.hr_lookup import name_to_initial

ROOT_NAME = "ICT-BG"

PERSONNEL = [
    # 云核心网产品线 / 云核心网研发管理部
    ("10001", "张明", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10002", "李华", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10003", "王芳", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10004", "赵强", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10005", "刘洋", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10006", "陈静", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    # 云核心网产品线 / 云核心网测试部
    ("10007", "周磊", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10008", "吴敏", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10009", "郑凯", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    # 产品规划部
    ("10010", "孙莉", ["ICT-BG", "产品规划部"]),
    ("10011", "黄磊", ["ICT-BG", "产品规划部"]),
    ("10012", "林涛", ["ICT-BG", "产品规划部"]),
    ("10013", "何婷", ["ICT-BG", "产品规划部"]),
    # 市场拓展部
    ("10014", "马超", ["ICT-BG", "市场拓展部"]),
    ("10015", "韩雪", ["ICT-BG", "市场拓展部"]),
    ("10016", "唐斌", ["ICT-BG", "市场拓展部"]),
]

EXTRA_DEPARTMENTS = [
    (ROOT_NAME, "产品规划部"),
    (ROOT_NAME, "市场拓展部"),
    ("云核心网产品线", "云核心网测试部"),
]

ZONE_YELLOW = {
    "10001": "gpt-4o-mini,claude-3-haiku",
    "10002": "gpt-4o-mini",
    "10003": "gpt-4o-mini",
    "10006": "gpt-4o-mini",
    "10007": "gpt-4o-mini,claude-3-haiku",
    "10010": "gpt-4o-mini",
    "10011": "gpt-4o-mini",
    "10015": "gpt-4o-mini",
}

ZONE_BLUE = {
    "10001": "gpt-4o,claude-3-opus",
    "10002": "gpt-4o",
    "10008": "gpt-4o",
    "10010": "gpt-4o,claude-3-opus",
    "10014": "gpt-4o",
}

ZONE_GREEN = {
    "10001": "gpt-4o,claude-3-5-sonnet",
    "10007": "gpt-4o",
    "10010": "gpt-4o,claude-3-5-sonnet",
    "10014": "gpt-4o,claude-3-5-sonnet",
}


def _find_dept(db, parent_id: int | None, name: str) -> MetaDepartment | None:
    return (
        db.query(MetaDepartment)
        .filter(MetaDepartment.parent_id == parent_id, MetaDepartment.name == name)
        .first()
    )


def _ensure_department(db, parent_id: int | None, name: str) -> MetaDepartment:
    existing = _find_dept(db, parent_id, name)
    if existing:
        return existing
    dept = MetaDepartment(parent_id=parent_id, name=name)
    db.add(dept)
    db.flush()
    return dept


def _ensure_extra_departments(db) -> None:
    root = _find_dept(db, None, ROOT_NAME)
    if not root:
        raise RuntimeError(f"未找到根部门「{ROOT_NAME}」，请先在配置中心创建组织架构")

    for parent_name, child_name in EXTRA_DEPARTMENTS:
        if parent_name == ROOT_NAME:
            parent = root
        else:
            parent = _find_dept(db, root.id, parent_name)
            if not parent:
                parent = _ensure_department(db, root.id, parent_name)
        _ensure_department(db, parent.id, child_name)


def _personnel_fields(dept_path: list[str]) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for i in range(1, 8):
        fields[f"dept_l{i}_name"] = None
        fields[f"dept_l{i}_code"] = None
    for i, name in enumerate(dept_path[:7], 1):
        fields[f"dept_l{i}_name"] = name
        fields[f"dept_l{i}_code"] = f"D{i:02d}"
    return fields


def _upsert_personnel(db, emp_no: str, name: str, dept_path: list[str]) -> None:
    fields = _personnel_fields(dept_path)
    person = db.get(MetaPersonnel, emp_no)
    if person:
        person.name = name
        person.name_initial = name_to_initial(name)
        for key, value in fields.items():
            setattr(person, key, value)
    else:
        db.add(
            MetaPersonnel(
                emp_no=emp_no,
                name=name,
                name_initial=name_to_initial(name),
                **fields,
            )
        )


def _upsert_zone(db, model_cls, mapping: dict[str, str]) -> None:
    for emp_no, models in mapping.items():
        row = db.get(model_cls, emp_no)
        if row:
            row.models = models
        else:
            db.add(model_cls(emp_no=emp_no, models=models))


def main() -> None:
    db = SessionLocal()
    try:
        _ensure_extra_departments(db)

        for emp_no, name, dept_path in PERSONNEL:
            if dept_path[0] != ROOT_NAME:
                raise RuntimeError(f"演示数据部门路径须以 {ROOT_NAME} 开头")
            _upsert_personnel(db, emp_no, name, dept_path)

        _upsert_zone(db, PermZoneYellow, ZONE_YELLOW)
        _upsert_zone(db, PermZoneBlue, ZONE_BLUE)
        _upsert_zone(db, PermZoneGreen, ZONE_GREEN)

        db.commit()
        print(f"已写入 {len(PERSONNEL)} 名演示人员")
        print(f"  黄区白名单: {len(ZONE_YELLOW)} 人（覆盖率 {len(ZONE_YELLOW)}/{len(PERSONNEL)} = {len(ZONE_YELLOW)/len(PERSONNEL)*100:.1f}%）")
        print(f"  蓝区白名单: {len(ZONE_BLUE)} 人（覆盖率 {len(ZONE_BLUE)}/{len(PERSONNEL)} = {len(ZONE_BLUE)/len(PERSONNEL)*100:.1f}%）")
        print(f"  绿区白名单: {len(ZONE_GREEN)} 人（覆盖率 {len(ZONE_GREEN)}/{len(PERSONNEL)} = {len(ZONE_GREEN)/len(PERSONNEL)*100:.1f}%）")
        print("请到配置中心 → 黄/蓝/绿区白名单 → 权限统计图 查看效果")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
