#!/usr/bin/env python3
"""插入演示用组织架构、人员、三区权限及使用统计，便于查看饼图/柱状图。

用法：cd backend && PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from app.database import SessionLocal, engine
from app.models import (
    MetaDepartment,
    MetaPersonnel,
    PermZoneBlue,
    PermZoneGreen,
    PermZoneYellow,

)
from app.services.hr_lookup import name_to_initial

# (dept_code, parent_dept_code, name)
ORG_DEPARTMENTS: list[tuple[str, str | None, str]] = [
    ("ICT-BG", None, "ICT-BG"),
    ("CCN-PL", "ICT-BG", "云核心网产品线"),
    ("CCN-RD", "CCN-PL", "云核心网研发管理部"),
    ("CCN-QA", "CCN-PL", "云核心网测试部"),
    ("PROD-PLAN", "ICT-BG", "产品规划部"),
    ("MKT-EXP", "ICT-BG", "市场拓展部"),
]

# 部门名称 -> 编码（写入人员 dept_lN_code）
DEPT_CODES = {name: code for code, _, name in ORG_DEPARTMENTS}

PERSONNEL: list[tuple[str, str, list[str]]] = [
    # 研发部 8 人
    ("10001", "张明", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10002", "李华", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10003", "王芳", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10004", "赵强", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10005", "刘洋", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10006", "陈静", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10017", "杨帆", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    ("10018", "朱丽", ["ICT-BG", "云核心网产品线", "云核心网研发管理部"]),
    # 测试部 5 人
    ("10007", "周磊", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10008", "吴敏", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10009", "郑凯", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10019", "冯杰", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    ("10020", "许娜", ["ICT-BG", "云核心网产品线", "云核心网测试部"]),
    # 产品规划 5 人
    ("10010", "孙莉", ["ICT-BG", "产品规划部"]),
    ("10011", "黄磊", ["ICT-BG", "产品规划部"]),
    ("10012", "林涛", ["ICT-BG", "产品规划部"]),
    ("10013", "何婷", ["ICT-BG", "产品规划部"]),
    ("10021", "罗斌", ["ICT-BG", "产品规划部"]),
    # 市场拓展 5 人
    ("10014", "马超", ["ICT-BG", "市场拓展部"]),
    ("10015", "韩雪", ["ICT-BG", "市场拓展部"]),
    ("10016", "唐斌", ["ICT-BG", "市场拓展部"]),
    ("10022", "邓伟", ["ICT-BG", "市场拓展部"]),
    ("10023", "曹颖", ["ICT-BG", "市场拓展部"]),
]

ZONE_YELLOW: dict[str, str] = {
    "10023": "gpt-4o-mini",
    "10001": "gpt-4o-mini,claude-3-haiku",
    "10002": "gpt-4o-mini",
    "10003": "gpt-4o-mini",
    "10005": "gpt-4o-mini",
    "10006": "gpt-4o-mini",
    "10007": "gpt-4o-mini,claude-3-haiku",
    "10008": "gpt-4o-mini",
    "10010": "gpt-4o-mini",
    "10011": "gpt-4o-mini",
    "10012": "gpt-4o-mini",
    "10014": "gpt-4o-mini",
    "10015": "gpt-4o-mini",
    "10017": "gpt-4o-mini",
    "10019": "gpt-4o-mini",
}

ZONE_BLUE: dict[str, str] = {
    "10001": "gpt-4o,claude-3-opus",
    "10002": "gpt-4o",
    "10004": "gpt-4o",
    "10007": "gpt-4o",
    "10008": "gpt-4o",
    "10010": "gpt-4o,claude-3-opus",
    "10011": "gpt-4o",
    "10013": "gpt-4o",
    "10014": "gpt-4o",
    "10016": "gpt-4o",
    "10018": "gpt-4o",
    "10021": "gpt-4o",
}

ZONE_GREEN: dict[str, str] = {
    "10001": "gpt-4o,claude-3-5-sonnet",
    "10003": "gpt-4o,claude-3-5-sonnet",
    "10007": "gpt-4o",
    "10009": "gpt-4o",
    "10010": "gpt-4o,claude-3-5-sonnet",
    "10012": "gpt-4o",
    "10014": "gpt-4o,claude-3-5-sonnet",
    "10015": "gpt-4o",
    "10020": "gpt-4o",
    "10022": "gpt-4o,claude-3-5-sonnet",
}

# 使用次数：拉开差距便于饼图/柱状图对比（详见 seed_usage_data.py）
USAGE_COUNTS: dict[str, int] = {
    "10001": 356,
    "10002": 245,
    "10003": 120,
    "10004": 0,
    "10005": 8,
    "10006": 189,
    "10007": 412,
    "10008": 67,
    "10009": 0,
    "10010": 278,
    "10011": 156,
    "10012": 0,
    "10013": 34,
    "10014": 198,
    "10015": 0,
    "10016": 92,
    "10017": 15,
    "10018": 0,
    "10019": 73,
    "10020": 5,
    "10021": 0,
    "10022": 301,
    "10023": 88,
}


def _migrate_meta_department_table(db) -> None:
    """旧表为 id/parent_id 时重建为 dept_code 结构"""
    inspector = inspect(engine)
    if "meta_department" not in inspector.get_table_names():
        MetaDepartment.__table__.create(bind=engine)
        return

    columns = {col["name"] for col in inspector.get_columns("meta_department")}
    if "dept_code" in columns:
        return

    print("检测到旧版 meta_department 表结构，正在重建…")
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    db.execute(text("DROP TABLE IF EXISTS meta_department"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.commit()
    MetaDepartment.__table__.create(bind=engine)
    print("meta_department 表已重建")


def _seed_org_tree(db) -> None:
    db.query(MetaDepartment).delete()
    db.flush()
    for dept_code, parent_dept_code, name in ORG_DEPARTMENTS:
        db.add(
            MetaDepartment(
                dept_code=dept_code,
                parent_dept_code=parent_dept_code,
                name=name,
            )
        )
    db.flush()


def _personnel_fields(dept_path: list[str]) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for i in range(1, 8):
        fields[f"dept_l{i}_name"] = None
        fields[f"dept_l{i}_code"] = None
    for i, name in enumerate(dept_path[:7], 1):
        fields[f"dept_l{i}_name"] = name
        fields[f"dept_l{i}_code"] = DEPT_CODES.get(name)
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


def _upsert_usage(db, mapping: dict[str, int]) -> None:
    """兼容旧版 stat_usage 表（可能无 imported_at 列）"""
    for emp_no, usage_count in mapping.items():
        db.execute(
            text(
                """
                INSERT INTO stat_usage (emp_no, usage_count)
                VALUES (:emp_no, :usage_count)
                ON DUPLICATE KEY UPDATE usage_count = :usage_count
                """
            ),
            {"emp_no": emp_no, "usage_count": usage_count},
        )


def main() -> None:
    db = SessionLocal()
    try:
        _migrate_meta_department_table(db)
        _seed_org_tree(db)

        for emp_no, name, dept_path in PERSONNEL:
            _upsert_personnel(db, emp_no, name, dept_path)

        _upsert_zone(db, PermZoneYellow, ZONE_YELLOW)
        _upsert_zone(db, PermZoneBlue, ZONE_BLUE)
        _upsert_zone(db, PermZoneGreen, ZONE_GREEN)
        _upsert_usage(db, USAGE_COUNTS)

        db.commit()

        total = len(PERSONNEL)
        print(f"已写入组织架构 {len(ORG_DEPARTMENTS)} 个节点")
        print(f"已写入演示人员 {total} 名")
        print(
            f"  黄区白名单: {len(ZONE_YELLOW)} 人"
            f"（覆盖率 {len(ZONE_YELLOW) / total * 100:.1f}%）"
        )
        print(
            f"  蓝区白名单: {len(ZONE_BLUE)} 人"
            f"（覆盖率 {len(ZONE_BLUE) / total * 100:.1f}%）"
        )
        print(
            f"  绿区白名单: {len(ZONE_GREEN)} 人"
            f"（覆盖率 {len(ZONE_GREEN) / total * 100:.1f}%）"
        )
        used = sum(1 for c in USAGE_COUNTS.values() if c > 0)
        print(f"  使用统计: {len(USAGE_COUNTS)} 人（已使用 {used}，未使用 {len(USAGE_COUNTS) - used}）")
        print()
        print("查看方式：")
        print("  配置中心 → 组织架构")
        print("  配置中心 → 黄/蓝/绿区白名单 → 权限统计图")
        print("  使用统计 → 统计图表")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
