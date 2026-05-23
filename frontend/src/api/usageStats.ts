import type {
  UsageImportFailureItem,
  UsageStatImportResponse,
  UsageStatListResponse
} from '@/types'

const BASE = '/api'

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, options)

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

async function downloadBlob(url: string, filename: string, options?: RequestInit) {
  const res = await fetch(`${BASE}${url}`, options)
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || '下载失败')
  }
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.click()
  URL.revokeObjectURL(objectUrl)
}

export const usageStatsApi = {
  list: () => requestJson<UsageStatListResponse>('/usage-stats'),

  importExcel: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return requestJson<UsageStatImportResponse>('/usage-stats/import', {
      method: 'POST',
      body: form
    })
  },

  downloadTemplate: () =>
    downloadBlob('/usage-stats/template', 'usage_stats_template.xlsx'),

  exportExceptions: (failures: UsageImportFailureItem[]) =>
    downloadBlob('/usage-stats/export-exceptions', `usage_import_exceptions_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ failures })
    })
}
