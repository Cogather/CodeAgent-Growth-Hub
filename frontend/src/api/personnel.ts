import type {
  ImportFailureItem,
  PersonnelBatchImportResponse,
  PersonnelItem,
  PersonnelListResponse,
  PersonnelUpdatePayload
} from '@/types'

const BASE = '/api'

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
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

export const personnelApi = {
  list: () => requestJson<PersonnelListResponse>('/personnel'),

  batchImport: (empNosText: string) =>
    requestJson<PersonnelBatchImportResponse>('/personnel/batch-import', {
      method: 'POST',
      body: JSON.stringify({ emp_nos_text: empNosText })
    }),

  update: (empNo: string, payload: PersonnelUpdatePayload) =>
    requestJson<PersonnelItem>(`/personnel/${encodeURIComponent(empNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),

  remove: (empNo: string) =>
    requestJson<void>(`/personnel/${encodeURIComponent(empNo)}`, { method: 'DELETE' }),

  exportExceptions: async (failures: ImportFailureItem[]) => {
    const res = await fetch(`${BASE}/personnel/export-exceptions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ failures })
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || '导出失败')
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `人员导入异常_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
  }
}
