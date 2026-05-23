const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })

  if (res.status === 204) {
    return undefined as T
  }

  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = data.detail
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join('；')
          : `请求失败 (${res.status})`
    throw new Error(message)
  }
  return data as T
}

export const departmentApi = {
  getRootStatus: () => request<import('@/types').RootStatus>('/departments/root-status'),
  getTree: () => request<import('@/types').DepartmentNode[]>('/departments/tree'),
  create: (payload: { parent_id: number | null; name: string }) =>
    request<import('@/types').DepartmentNode>('/departments', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  update: (id: number, payload: { name: string }) =>
    request<import('@/types').DepartmentNode>(`/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),
  remove: (id: number) => request<void>(`/departments/${id}`, { method: 'DELETE' })
}
