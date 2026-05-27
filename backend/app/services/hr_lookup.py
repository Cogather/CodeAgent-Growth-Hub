"""HR 系统工号查询：GET ?info=工号，解析 JSON 数组中的员工与六级部门"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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
    raw: dict[str, Any] = field(default_factory=dict)


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


def _hr_org_start_level() -> int:
    return get_settings().hr_org_start_level


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
    """界面展示工号：与库中 emp_no（sAMAccountName）一致，不再拼接姓名首字母"""
    _ = name
    return emp_no.strip()


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


def org_dept_names_from_record(record: dict[str, Any]) -> list[str]:
    """与组织架构对齐的部门名称路径（默认自 hwDepartName3 起）"""
    start = _hr_org_start_level()
    names: list[str] = []
    for i in range(start, HR_API_DEPT_LEVELS + 1):
        name = _str_value(record.get(f"hwDepartName{i}"))
        if name:
            names.append(name)
    return names


def count_org_dept_levels(record: dict[str, Any]) -> int:
    start = _hr_org_start_level()
    count = 0
    for i in range(start, HR_API_DEPT_LEVELS + 1):
        if _str_value(record.get(f"hwDepartName{i}")) or _str_value(record.get(f"hwDepartCode{i}")):
            count += 1
    return count


def hr_record_to_personnel_fields(record: dict[str, Any]) -> dict[str, str | None]:
    """hwDepartName1-6 原样写入 dept_l1-6；展示与组织树自第 3 级起由前端/筛选处理"""
    data: dict[str, str | None] = {}
    for i in range(1, DEPT_LEVELS + 1):
        data[f"dept_l{i}_name"] = None
        data[f"dept_l{i}_code"] = None

    for hr_i in range(1, HR_API_DEPT_LEVELS + 1):
        dname = _str_value(record.get(f"hwDepartName{hr_i}"))
        dcode = _str_value(record.get(f"hwDepartCode{hr_i}"))
        if not dname and not dcode:
            continue
        data[f"dept_l{hr_i}_name"] = dname or None
        data[f"dept_l{hr_i}_code"] = dcode or None
    return data


def personnel_fields_from_employee(hr: HREmployee) -> dict[str, str | None]:
    if hr.raw:
        return hr_record_to_personnel_fields(hr.raw)
    return hr_levels_to_model_fields(hr.dept_levels)


def org_dept_names_from_employee(hr: HREmployee) -> list[str]:
    if hr.raw:
        return org_dept_names_from_record(hr.raw)
    return dept_levels_to_names(hr.dept_levels)


def _sam_account_name(record: dict[str, Any]) -> str:
    for key in ("sAMAccountName", "samAccountName", "SamAccountName"):
        value = _str_value(record.get(key))
        if value:
            return value
    return ""


def personnel_emp_no_from_record(record: dict[str, Any], query_emp_no: str) -> str | None:
    """人员名单主键取 HR 的 sAMAccountName；未配置真实 HR 时回退为查询工号（Mock）"""
    account = _sam_account_name(record)
    if account:
        return account
    if get_settings().hr_lookup_url:
        return None
    return query_emp_no.strip() or None


def _parse_hr_record(record: dict[str, Any], query_emp_no: str) -> HREmployee | None:
    name = _str_value(record.get("chName"))
    if not name:
        return None

    emp_no = personnel_emp_no_from_record(record, query_emp_no)
    if not emp_no:
        return None

    dept_levels: list[HRDeptLevel] = []
    for i in range(1, HR_API_DEPT_LEVELS + 1):
        dname = _str_value(record.get(f"hwDepartName{i}"))
        dcode = _str_value(record.get(f"hwDepartCode{i}"))
        if dname or dcode:
            dept_levels.append(HRDeptLevel(name=dname, code=dcode))

    return HREmployee(emp_no=emp_no, name=name, dept_levels=dept_levels, raw=record)


def _lookup_employee_remote(emp_no: str) -> HREmployee | None:
    settings = get_settings()
    url = settings.hr_lookup_url
    if not url:
        return None

    request_url = _build_lookup_url(url, emp_no)
    try:
        with httpx.Client(
            timeout=settings.hr_lookup_timeout_seconds,
            trust_env=False,
            verify=False,
        ) as client:
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

    if not _sam_account_name(record):
        logger.warning("HR record missing sAMAccountName for query %s", emp_no)
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
    """Mock 数据等无 raw 记录时，按顺序写入 dept_l1 起"""
    data: dict[str, str | None] = {}
    for i in range(1, DEPT_LEVELS + 1):
        data[f"dept_l{i}_name"] = None
        data[f"dept_l{i}_code"] = None
    for i, lv in enumerate(levels[:DEPT_LEVELS], 1):
        data[f"dept_l{i}_name"] = lv.name
        data[f"dept_l{i}_code"] = lv.code
    return data
