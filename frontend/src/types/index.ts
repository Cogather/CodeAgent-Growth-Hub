export interface User {
  id: number
  username: string
  name: string
  department: string
  role: 'user' | 'admin'
}

export interface Department {
  id: number
  name: string
  parentId: number | null
  children?: Department[]
}

export type ZoneType = 'yellow' | 'blue' | 'green'

export type RequestStatus = 'pending' | 'processing' | 'completed' | 'rejected'

export interface AccessRequest {
  id: number
  requestNo: string
  zone: ZoneType
  tool: string
  model: string
  status: RequestStatus
  submitter: string
  submitterName: string
  createdAt: string
  updatedAt: string
  processor?: string
  remark?: string
  accounts: AccessRequestAccount[]
}

export interface AccessRequestAccount {
  id: number
  requestId: number
  username: string
  status: RequestStatus
}

export interface UsageStats {
  id: number
  username: string
  name: string
  department: string
  zone: ZoneType
  tool: string
  callCount: number
  activeDays: number
  isDeepUser: boolean
  date: string
}

export type TicketStatus = 'pending' | 'processing' | 'resolved' | 'closed'
export type TicketCategory = 'bug' | 'feature' | 'question' | 'optimization'

export interface Ticket {
  id: number
  ticketNo: string
  title: string
  category: TicketCategory
  status: TicketStatus
  submitter: string
  submitterName: string
  processor: string
  processorName: string
  department: string
  link: string
  createdAt: string
  updatedAt: string
}

export type ArtifactCategory = 'skill' | 'mcp' | 'bestpractice'

export interface Artifact {
  id: number
  name: string
  description: string
  link: string
  publisher: string
  publisherName: string
  publisherDept: string
  category: ArtifactCategory
  createdAt: string
}

export type DeepUserRule = {
  callCountThreshold: number
  activeDaysThreshold: number
  daysWindow: number
}

export interface AuditLog {
  id: number
  action: string
  operator: string
  operatorName: string
  target: string
  detail: string
  createdAt: string
}

export interface DictItem {
  id: number
  type: string
  label: string
  value: string
  sort: number
}

export interface OrganizationUnit {
  id: number
  name: string
  type: 'pdu' | 'devDept' | 'fse' | 'testField'
  parentId: number | null
  pduContact?: string
  devContact?: string
  owner?: string
  responsible?: string
  createdAt: string
  updatedAt: string
}

export interface FSE {
  id: number
  name: string
  pduId: number
  pduName: string
  createdAt: string
  updatedAt: string
}

export interface Personnel {
  id: number
  employeeNo: string
  name: string
  pduId?: number
  pduName?: string
  devDeptId?: number
  devDeptName?: string
  testFieldId?: number
  testFieldName?: string
  pduContact?: string
  devContact?: string
  fse?: string
  zones: PersonnelZone[]
  createdAt: string
  updatedAt: string
}

export interface PersonnelZone {
  zone: ZoneType
  modelPermission: string
  toolPermission: string
  batchDate: string
}

export interface DailyUsage {
  id: number
  personnelId: number
  employeeNo: string
  name: string
  date: string
  callCount: number
  usedCodeAgent: boolean
}

export interface UsageSummary {
  totalPersonnel: number
  hasPermissionCount: number
  usedCount: number
  topUserCount: number
  seniorUserCount: number
  byPdu: { pduName: string; total: number; hasPermission: number; used: number; top: number; senior: number }[]
  byDevDept: { devDeptName: string; total: number; hasPermission: number; used: number; top: number; senior: number }[]
  byTestField: { testFieldName: string; total: number; hasPermission: number; used: number; top: number; senior: number }[]
}
