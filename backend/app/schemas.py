from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import DEPT_LEVELS


class DepartmentCreate(BaseModel):
    dept_code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    parent_dept_code: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class DepartmentNode(BaseModel):
    dept_code: str
    parent_dept_code: Optional[str]
    name: str
    children: List["DepartmentNode"] = []


class DepartmentLazyNode(BaseModel):
    dept_code: str
    parent_dept_code: Optional[str]
    name: str
    has_children: bool


class DepartmentFlat(BaseModel):
    dept_code: str
    parent_dept_code: Optional[str]
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
    total: int
    page: int
    page_size: int


class PersonnelDistinctResponse(BaseModel):
    values: List[str]


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


class ZonePermissionItem(PersonnelDeptFields):
    emp_no: str
    display_emp_no: str
    name: str
    models: List[str]


class ZonePermissionListResponse(BaseModel):
    zone: str
    zone_label: str
    items: List[ZonePermissionItem]
    total: int
    total_all: int
    page: int
    page_size: int


class ZoneEmpNosResponse(BaseModel):
    emp_nos: List[str]


class ZoneExportFailuresRequest(BaseModel):
    failures: List[ZoneImportFailureItem]


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
    total: int
    total_all: int
    page: int
    page_size: int
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


class UsageExportZeroUsageRequest(BaseModel):
    dept_path: List[str] = Field(default_factory=list, description="部门路径，空表示全部有权限人员")


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class AuthUser(BaseModel):
    id: int
    username: str
    name: str
    role: str
    must_change_password: bool


class SysUserItem(BaseModel):
    id: int
    username: str
    name: str
    role: str
    is_active: bool
    must_change_password: bool
    created_at: str
    updated_at: str


class SysUserListResponse(BaseModel):
    items: List[SysUserItem]


class SysUserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    role: str = Field(default="viewer", pattern="^(admin|viewer)$")
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class SysUserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    role: Optional[str] = Field(default=None, pattern="^(admin|viewer)$")
    is_active: Optional[bool] = None


class SysUserCreateResponse(BaseModel):
    user: SysUserItem
    temporary_password: str


class SysUserResetPasswordResponse(BaseModel):
    temporary_password: str
