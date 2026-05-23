import { requestJson } from '@/api/client'
import type { DepartmentNode, RootStatus } from '@/types'

export const departmentApi = {
  getRootStatus: () => requestJson<RootStatus>('/departments/root-status'),
  getTree: () => requestJson<DepartmentNode[]>('/departments/tree'),
  create: (payload: { parent_id: number | null; name: string }) =>
    requestJson<DepartmentNode>('/departments', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  update: (id: number, payload: { name: string }) =>
    requestJson<DepartmentNode>(`/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),
  remove: (id: number) => requestJson<void>(`/departments/${id}`, { method: 'DELETE' })
}
