#!/usr/bin/env python3
"""演示「重点关注 PDU」：扩展四级部门、调整人员归属、写入关注列表。

前置：已运行 seed_demo_data.py（组织树与人员基础数据）。

用法：cd backend && PYTHONPATH=. .venv/bin/python scripts/seed_focus_pdu_demo.py
"""

from __future__ import annotations

from app.database import SessionLocal
from app.models import MetaDepartment, MetaFocusPdu, MetaPersonnel
from app.services.hr_lookup import name_to_initial

# 四级 PDU（父节点须已存在于 seed_demo_data）
EXTRA_DEPARTMENTS: list[tuple[str, str, str]] = [
    ("CCN-RD-PDU-PLAT", "CCN-RD", "平台PDU"),
    ("CCN-RD-PDU-PROTO", "CCN-RD", "协议PDU"),
    ("CCN-QA-PDU-AUTO", "CCN-QA", "自动化PDU"),
]

FOCUS_PDU_CODES = ["CCN-RD-PDU-PLAT", "CCN-RD-PDU-PROTO"]

DEPT_CODES = {
    "ICT-BG": "ICT-BG",
    "云核心网产品线": "CCN-PL",
    "云核心网研发管理部": "CCN-RD",
    "云核心网测试部": "CCN-QA",
    "平台PDU": "CCN-RD-PDU-PLAT",
    "协议PDU": "CCN-RD-PDU-PROTO",
    "自动化PDU": "CCN-QA-PDU-AUTO",
}

# 工号 -> 新部门路径（含四级 PDU）
PERSONNEL_PATHS: dict[str, list[str]] = {
    "10001": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "平台PDU"],
    "10002": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "平台PDU"],
    "10003": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "平台PDU"],
    "10004": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "平台PDU"],
    "10005": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "协议PDU"],
    "10006": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "协议PDU"],
    "10017": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "平台PDU"],
    "10018": ["ICT-BG", "云核心网产品线", "云核心网研发管理部", "协议PDU"],
    "10007": ["ICT-BG", "云核心网产品线", "云核心网测试部", "自动化PDU"],
    "10008": ["ICT-BG", "云核心网产品线", "云核心网测试部", "自动化PDU"],
    "10009": ["ICT-BG", "云核心网产品线", "云核心网测试部", "自动化PDU"],
    "10019": ["ICT-BG", "云核心网产品线", "云核心网测试部", "自动化PDU"],
    "10020": ["ICT-BG", "云核心网产品线", "云核心网测试部", "自动化PDU"],
}


def _personnel_fields(dept_path: list[str]) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for i in range(1, 8):
        fields[f"dept_l{i}_name"] = None
        fields[f"dept_l{i}_code"] = None
    for i, name in enumerate(dept_path[:7], 1):
        fields[f"dept_l{i}_name"] = name
        fields[f"dept_l{i}_code"] = DEPT_CODES.get(name)
    return fields


def main() -> None:
    db = SessionLocal()
    try:
        for dept_code, parent, name in EXTRA_DEPARTMENTS:
            if db.get(MetaDepartment, dept_code) is None:
                db.add(
                    MetaDepartment(dept_code=dept_code, parent_dept_code=parent, name=name)
                )
        db.flush()

        for emp_no, path in PERSONNEL_PATHS.items():
            person = db.get(MetaPersonnel, emp_no)
            if person is None:
                print(f"跳过未知工号 {emp_no}，请先运行 seed_demo_data.py")
                continue
            fields = _personnel_fields(path)
            for key, value in fields.items():
                setattr(person, key, value)

        db.query(MetaFocusPdu).delete()
        for i, code in enumerate(FOCUS_PDU_CODES):
            db.add(MetaFocusPdu(dept_code=code, alias=None, sort_order=i))

        db.commit()
        print("已写入四级 PDU 部门、更新人员路径，并设置关注：", ", ".join(FOCUS_PDU_CODES))
        print("开启 PDU 视角后：人员名单约 8 人（两个研发 PDU）；关闭为全员 23 人（演示数据）。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
