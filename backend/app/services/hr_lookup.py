"""HR 系统工号查询（Mock，后续替换为真实接口）"""

from __future__ import annotations

from dataclasses import dataclass

from pypinyin import lazy_pinyin

from app.models import DEPT_LEVELS


@dataclass
class HRDeptLevel:
    name: str
    code: str


@dataclass
class HREmployee:
    emp_no: str
    name: str
    dept_levels: list[HRDeptLevel]


_MOCK_HR: dict[str, HREmployee] = {
    "10001": HREmployee(
        "10001",
        "张三",
        [HRDeptLevel("总公司", "ORG001"), HRDeptLevel("研发部", "RD001"), HRDeptLevel("后端组", "RD-BE")],
    ),
    "10002": HREmployee(
        "10002",
        "李四",
        [HRDeptLevel("总公司", "ORG001"), HRDeptLevel("研发部", "RD001")],
    ),
    "10003": HREmployee(
        "10003",
        "王五",
        [HRDeptLevel("总公司", "ORG001"), HRDeptLevel("产品部", "PD001")],
    ),
    "20001": HREmployee(
        "20001",
        "赵六",
        [HRDeptLevel("其他公司", "OTHER001"), HRDeptLevel("研发部", "RD001")],
    ),
    "20002": HREmployee(
        "20002",
        "钱七",
        [HRDeptLevel("总公司", "ORG001"), HRDeptLevel("未配置部门", "XX001")],
    ),
}


def name_to_initial(name: str) -> str:
    name = name.strip()
    if not name:
        return "X"
    if name[0].isascii() and name[0].isalpha():
        return name[0].upper()
    py = lazy_pinyin(name[0])
    if py and py[0]:
        return py[0][0].upper()
    return "X"


def display_emp_no(name: str, emp_no: str) -> str:
    return f"{name_to_initial(name)}{emp_no}"


def lookup_employee(emp_no: str) -> HREmployee | None:
    return _MOCK_HR.get(emp_no.strip())


def dept_levels_to_names(levels: list[HRDeptLevel]) -> list[str]:
    return [lv.name for lv in levels]


def hr_levels_to_model_fields(levels: list[HRDeptLevel]) -> dict[str, str | None]:
    """将 HR 层级列表写入 meta_personnel 平铺字段"""
    data: dict[str, str | None] = {}
    for i in range(1, DEPT_LEVELS + 1):
        data[f"dept_l{i}_name"] = None
        data[f"dept_l{i}_code"] = None
    for i, lv in enumerate(levels[:DEPT_LEVELS], 1):
        data[f"dept_l{i}_name"] = lv.name
        data[f"dept_l{i}_code"] = lv.code
    return data
