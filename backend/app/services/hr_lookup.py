"""HR 系统工号查询：GET ?info=工号，解析 JSON 数组中的员工与六级部门"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
from pypinyin import lazy_pinyin

from app.config import get_settings
from app.models import DEPT_LEVELS

logger = logging.getLogger(__name__)

HR_API_DEPT_LEVELS = 6

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


def _build_lookup_url(base: str, emp_no: str) -> str:
    base = base.strip()
    encoded = quote(emp_no.strip(), safe="")
    if base.endswith("?info="):
        return f"{base}{encoded}"
    if base.endswith("?info"):
        return f"{base}={encoded}"
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}info={encoded}"


def _str_value(raw: Any) -> str:
    if raw is None:
        return ""
    return str(raw).strip()


def _pick_record(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """HR 返回 JSON 数组时默认取第一条；空数组表示查无此人"""
    return items[0] if items else None


def _parse_hr_record(record: dict[str, Any], emp_no: str) -> HREmployee | None:
    name = _str_value(record.get("chName"))
    if not name:
        return None

    dept_levels: list[HRDeptLevel] = []
    for i in range(1, HR_API_DEPT_LEVELS + 1):
        dname = _str_value(record.get(f"hwDepartName{i}"))
        dcode = _str_value(record.get(f"hwDepartCode{i}"))
        if dname or dcode:
            dept_levels.append(HRDeptLevel(name=dname, code=dcode))

    return HREmployee(emp_no=emp_no.strip(), name=name, dept_levels=dept_levels)


def _lookup_employee_remote(emp_no: str) -> HREmployee | None:
    settings = get_settings()
    url = settings.hr_lookup_url
    if not url:
        return None

    request_url = _build_lookup_url(url, emp_no)
    try:
        with httpx.Client(timeout=settings.hr_lookup_timeout_seconds) as client:
            response = client.get(request_url)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("HR lookup HTTP error for %s: %s", emp_no, exc)
        return None
    except ValueError as exc:
        logger.warning("HR lookup invalid JSON for %s: %s", emp_no, exc)
        return None

    if not isinstance(payload, list):
        logger.warning("HR lookup expected JSON array for %s, got %s", emp_no, type(payload).__name__)
        return None

    record = _pick_record(payload)
    if not record:
        return None

    return _parse_hr_record(record, emp_no)


def lookup_employee(emp_no: str) -> HREmployee | None:
    emp_no = emp_no.strip()
    if not emp_no:
        return None

    if get_settings().hr_lookup_url:
        return _lookup_employee_remote(emp_no)

    return _MOCK_HR.get(emp_no)


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
