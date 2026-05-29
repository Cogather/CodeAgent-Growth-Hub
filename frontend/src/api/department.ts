import { requestJson } from '@/api/client'
import type { DepartmentLazyNode, DepartmentNode, RootStatus } from '@/types'

export const departmentApi = {
  getRootStatus: () => requestJson<RootStatus>('/departments/root-status'),
  getTree: () => requestJson<DepartmentNode[]>('/departments/tree'),
  getChildren: (parentDeptCode?: string | null) => {
    const query = parentDeptCode ? `?parent_dept_code=${encodeURIComponent(parentDeptCode)}` : ''
    return requestJson<DepartmentLazyNode[]>(`/departments/children${query}`)
  },
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
