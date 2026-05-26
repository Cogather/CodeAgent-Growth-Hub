import { requestJson } from '@/api/client'
import type { DepartmentNode, RootStatus } from '@/types'

export const departmentApi = {
  getRootStatus: () => requestJson<RootStatus>('/departments/root-status'),
  getTree: () => requestJson<DepartmentNode[]>('/departments/tree'),
  create: (payload: { dept_code: string; parent_dept_code: string | null; name: string }) =>
    requestJson<DepartmentNode>('/departments', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  update: (deptCode: string, payload: { name: string }) =>
    requestJson<DepartmentNode>(`/departments/${encodeURIComponent(deptCode)}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),
  remove: (deptCode: string) =>
    requestJson<void>(`/departments/${encodeURIComponent(deptCode)}`, { method: 'DELETE' })
}
