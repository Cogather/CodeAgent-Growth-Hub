from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import DEPT_LEVELS


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    parent_id: Optional[int] = None


class DepartmentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class DepartmentNode(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    children: List["DepartmentNode"] = []


class DepartmentFlat(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str

    model_config = {"from_attributes": True}


class RootStatus(BaseModel):
    has_root: bool


class PersonnelDeptFields(BaseModel):
    dept_l1_name: Optional[str] = None
    dept_l1_code: Optional[str] = None
    dept_l2_name: Optional[str] = None
    dept_l2_code: Optional[str] = None
    dept_l3_name: Optional[str] = None
    dept_l3_code: Optional[str] = None
    dept_l4_name: Optional[str] = None
    dept_l4_code: Optional[str] = None
    dept_l5_name: Optional[str] = None
    dept_l5_code: Optional[str] = None
    dept_l6_name: Optional[str] = None
    dept_l6_code: Optional[str] = None
    dept_l7_name: Optional[str] = None
    dept_l7_code: Optional[str] = None


class PersonnelItem(PersonnelDeptFields):
    emp_no: str
    display_emp_no: str
    name: str


class PersonnelListResponse(BaseModel):
    items: List[PersonnelItem]


class PersonnelBatchImportRequest(BaseModel):
    emp_nos_text: str = Field(..., description="工号列表，逗号分隔")


class ImportFailureItem(BaseModel):
    emp_no: str
    name: Optional[str] = None
    hr_dept_path: Optional[List[str]] = None
    reason: str


class PersonnelBatchImportResponse(BaseModel):
    imported_count: int
    failures: List[ImportFailureItem]


class PersonnelUpdate(PersonnelDeptFields):
    name: str = Field(..., min_length=1, max_length=128)


class ExportExceptionsRequest(BaseModel):
    failures: List[ImportFailureItem]


class ZonePermissionItem(BaseModel):
    emp_no: str
    display_emp_no: str
    name: str
    models: List[str]


class ZonePermissionListResponse(BaseModel):
    zone: str
    zone_label: str
    items: List[ZonePermissionItem]


class ZonePermissionBatchRequest(BaseModel):
    emp_nos_text: str = Field(..., description="工号，逗号分隔")
    models_text: str = Field(..., description="模型，逗号分隔，应用于本批所有工号")


class ZoneImportFailureItem(BaseModel):
    emp_no: str
    reason: str


class ZonePermissionBatchResponse(BaseModel):
    upserted_count: int
    failures: List[ZoneImportFailureItem]


class ZonePermissionUpdate(BaseModel):
    models_text: str = Field(..., min_length=1, description="模型，逗号分隔")


class UsageStatItem(PersonnelDeptFields):
    emp_no: str
    display_emp_no: str
    name: str
    usage_count: int = 0


class UsageStatListResponse(BaseModel):
    items: List[UsageStatItem]
    imported_at: Optional[str] = None


class UsageImportFailureItem(BaseModel):
    emp_no: str
    usage_count: Optional[int] = None
    reason: str


class UsageStatImportResponse(BaseModel):
    imported_count: int
    failures: List[UsageImportFailureItem]


class UsageExportExceptionsRequest(BaseModel):
    failures: List[UsageImportFailureItem]
