#!/usr/bin/env python3
"""仅刷新使用统计数据（stat_usage），便于查看使用统计页饼图/柱状图。

用法：cd backend && PYTHONPATH=. .venv/bin/python scripts/seed_usage_data.py
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from app.database import SessionLocal, engine
from app.models import PermZoneYellow
from app.services.usage_roster import get_authorized_emp_nos

# 使用次数：刻意拉开差距，便于图表对比（0 = 未使用）
USAGE_COUNTS: dict[str, int] = {
    # 研发部
    "10001": 356,
    "10002": 245,
    "10003": 120,
    "10004": 0,
    "10005": 8,
    "10006": 189,
    "10017": 15,
    "10018": 0,
    # 测试部
    "10007": 412,
    "10008": 67,
    "10009": 0,
    "10019": 73,
    "10020": 5,
    # 产品规划
    "10010": 278,
    "10011": 156,
    "10012": 0,
    "10013": 34,
    "10021": 0,
    # 市场拓展
    "10014": 198,
    "10015": 0,
    "10016": 92,
    "10022": 301,
    "10023": 88,
}


def _ensure_stat_usage_schema(db) -> bool:
    """补齐 imported_at 列，与模型及导入逻辑一致"""
    columns = {col["name"] for col in inspect(engine).get_columns("stat_usage")}
    if "imported_at" in columns:
        return True
    print("stat_usage 表缺少 imported_at 列，正在添加…")
    db.execute(
        text(
            "ALTER TABLE stat_usage "
            "ADD COLUMN imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )
    )
    db.commit()
    return True


def _upsert_usage(db, mapping: dict[str, int], *, has_imported_at: bool) -> None:
    if has_imported_at:
        sql = """
            INSERT INTO stat_usage (emp_no, usage_count, imported_at)
            VALUES (:emp_no, :usage_count, NOW())
            ON DUPLICATE KEY UPDATE usage_count = :usage_count, imported_at = NOW()
        """
    else:
        sql = """
            INSERT INTO stat_usage (emp_no, usage_count)
            VALUES (:emp_no, :usage_count)
            ON DUPLICATE KEY UPDATE usage_count = :usage_count
        """
    for emp_no, usage_count in mapping.items():
        db.execute(text(sql), {"emp_no": emp_no, "usage_count": usage_count})


def _ensure_10023_in_yellow(db) -> None:
    """10023 若未在任何白名单，使用统计页不会展示"""
    if db.get(PermZoneYellow, "10023"):
        return
    if "10023" in get_authorized_emp_nos(db):
        return
    db.add(PermZoneYellow(emp_no="10023", models="gpt-4o-mini"))
    db.flush()


def main() -> None:
    db = SessionLocal()
    try:
        _ensure_10023_in_yellow(db)
        authorized = get_authorized_emp_nos(db)
        if not authorized:
            print("未找到有权限人员，请先运行 scripts/seed_demo_data.py")
            return

        to_write = {k: v for k, v in USAGE_COUNTS.items() if k in authorized}
        missing = authorized - set(to_write.keys())
        for emp_no in sorted(missing):
            to_write[emp_no] = 0

        has_imported_at = _ensure_stat_usage_schema(db)
        _upsert_usage(db, to_write, has_imported_at=has_imported_at)
        db.commit()

        used = sum(1 for c in to_write.values() if c > 0)
        total = len(to_write)
        print(f"已更新 {total} 人的使用次数")
        print(f"  有使用: {used} 人，未使用: {total - used} 人")
        print(f"  使用率: {used / total * 100:.1f}%")
        print(f"  最高: {max(to_write.values())} 次，最低（非零）: ", end="")
        non_zero = [c for c in to_write.values() if c > 0]
        print(f"{min(non_zero) if non_zero else 0} 次")
        print("请到「使用统计」→「统计图表」查看效果")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
