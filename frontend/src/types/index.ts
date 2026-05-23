export type UserRole = 'admin' | 'operator' | 'viewer'

export interface User {
  id: number
  username: string
  name: string
  department: string
  role: UserRole
}

export type ModuleStatus = 'ready' | 'developing' | 'planned'

export interface AppModule {
  key: string
  title: string
  description: string
  path: string
  icon: string
  owner?: string
  status: ModuleStatus
}

export interface ConfigItem {
  id: string
  key: string
  label: string
  value: string
  category: string
  description: string
  updatedAt: string
  updatedBy: string
}

export interface AuditLogEntry {
  id: string
  module: string
  action: string
  target: string
  operator: string
  createdAt: string
}

export interface DepartmentNode {
  id: number
  parent_id: number | null
  name: string
  children: DepartmentNode[]
}

export interface RootStatus {
  has_root: boolean
}

export interface PersonnelItem {
  emp_no: string
  display_emp_no: string
  name: string
  dept_l1_name: string | null
  dept_l1_code: string | null
  dept_l2_name: string | null
  dept_l2_code: string | null
  dept_l3_name: string | null
  dept_l3_code: string | null
  dept_l4_name: string | null
  dept_l4_code: string | null
  dept_l5_name: string | null
  dept_l5_code: string | null
  dept_l6_name: string | null
  dept_l6_code: string | null
  dept_l7_name: string | null
  dept_l7_code: string | null
}

export interface PersonnelListResponse {
  items: PersonnelItem[]
}

export interface ImportFailureItem {
  emp_no: string
  name?: string | null
  hr_dept_path?: string[] | null
  reason: string
}

export interface PersonnelBatchImportResponse {
  imported_count: number
  failures: ImportFailureItem[]
}

export type PersonnelUpdatePayload = Pick<
  PersonnelItem,
  | 'name'
  | 'dept_l1_name'
  | 'dept_l1_code'
  | 'dept_l2_name'
  | 'dept_l2_code'
  | 'dept_l3_name'
  | 'dept_l3_code'
  | 'dept_l4_name'
  | 'dept_l4_code'
  | 'dept_l5_name'
  | 'dept_l5_code'
  | 'dept_l6_name'
  | 'dept_l6_code'
  | 'dept_l7_name'
  | 'dept_l7_code'
>

export const DEPT_LEVELS = 7

export type NetworkZone = 'yellow' | 'blue' | 'green'

export interface ZonePermissionItem {
  emp_no: string
  display_emp_no: string
  name: string
  models: string[]
}

export interface ZonePermissionListResponse {
  zone: NetworkZone
  zone_label: string
  items: ZonePermissionItem[]
}

export interface ZoneImportFailureItem {
  emp_no: string
  reason: string
}

export interface ZonePermissionBatchResponse {
  upserted_count: number
  failures: ZoneImportFailureItem[]
}

export interface ZonePermissionUpdatePayload {
  models_text: string
}

export interface UsageStatItem extends Pick<
  PersonnelItem,
  | 'emp_no'
  | 'display_emp_no'
  | 'name'
  | 'dept_l1_name'
  | 'dept_l1_code'
  | 'dept_l2_name'
  | 'dept_l2_code'
  | 'dept_l3_name'
  | 'dept_l3_code'
  | 'dept_l4_name'
  | 'dept_l4_code'
  | 'dept_l5_name'
  | 'dept_l5_code'
  | 'dept_l6_name'
  | 'dept_l6_code'
  | 'dept_l7_name'
  | 'dept_l7_code'
> {
  usage_count: number
}

export interface UsageStatListResponse {
  items: UsageStatItem[]
  imported_at: string | null
}

export interface UsageImportFailureItem {
  emp_no: string
  usage_count: number | null
  reason: string
}

export interface UsageStatImportResponse {
  imported_count: number
  failures: UsageImportFailureItem[]
}

export const ZONE_META: Record<NetworkZone, { label: string; description: string }> = {
  yellow: { label: '黄区', description: '黄区人员白名单与模型权限' },
  blue: { label: '蓝区', description: '蓝区人员白名单与模型权限' },
  green: { label: '绿区', description: '绿区人员白名单与模型权限' }
}
