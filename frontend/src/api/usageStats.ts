import { downloadBlob, requestJson } from '@/api/client'
import type {
  UsageImportFailureItem,
  UsageStatImportResponse,
  UsageStatItem,
  UsageStatListParams,
  UsageStatListResponse
} from '@/types'

const buildListQuery = (params: UsageStatListParams = {}) => {
  const search = new URLSearchParams()
  if (params.page) search.set('page', String(params.page))
  if (params.page_size) search.set('page_size', String(params.page_size))
  if (params.q) search.set('q', params.q)
  for (const level of [3, 4, 5, 6] as const) {
    const key = `dept_l${level}_name` as const
    if (params[key] !== undefined) search.set(key, params[key]!)
  }
  const query = search.toString()
  return query ? `?${query}` : ''
}

export const usageStatsApi = {
  list: (params: UsageStatListParams = {}) =>
    requestJson<UsageStatListResponse>(`/usage-stats${buildListQuery(params)}`),

  listAll: async (params: Omit<UsageStatListParams, 'page' | 'page_size'> = {}) => {
    const pageSize = 200
    const all: UsageStatItem[] = []
    let page = 1
    let total = 0
    let importedAt: string | null = null

    while (true) {
      const data = await usageStatsApi.list({ ...params, page, page_size: pageSize })
      importedAt = data.imported_at
      total = data.total
      all.push(...data.items)
      if (all.length >= total || data.items.length === 0) break
      page += 1
    }

    return { items: all, total, imported_at: importedAt }
  },

  distinctValues: (field: string) =>
    requestJson<{ values: string[] }>(`/usage-stats/distinct/${encodeURIComponent(field)}`),

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
    }),

  exportZeroUsage: (deptPath: string[] = []) =>
    downloadBlob('/usage-stats/export-zero-usage', `usage_zero_users_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dept_path: deptPath })
    })
}
