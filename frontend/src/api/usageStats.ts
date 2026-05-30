import { downloadBlob, requestJson, type FetchOptions } from '@/api/client'
import { appendFocusPduOnly } from '@/utils/focusPduQuery'
import type {
  UsageImportFailureItem,
  UsageStatImportResponse,
  UsageStatItem,
  UsageStatListParams,
  UsageStatListResponse
} from '@/types'

/** 列表/筛选项；大表 count 可能较慢 */
const USAGE_LIST_TIMEOUT_MS = 60_000
/** Excel 全量导入、零使用导出、图表拉全量分页 */
const USAGE_HEAVY_TIMEOUT_MS = 120_000

const usageRequest = <T>(url: string, options?: FetchOptions) =>
  requestJson<T>(url, { timeoutMs: USAGE_LIST_TIMEOUT_MS, ...options })

const buildListQuery = (params: UsageStatListParams = {}) => {
  const search = new URLSearchParams()
  if (params.page) search.set('page', String(params.page))
  if (params.page_size) search.set('page_size', String(params.page_size))
  if (params.q) search.set('q', params.q)
  for (const level of [3, 4, 5, 6] as const) {
    const key = `dept_l${level}_name` as const
    if (params[key] !== undefined) search.set(key, params[key]!)
  }
  appendFocusPduOnly(search, Boolean(params.focus_pdu_only))
  const query = search.toString()
  return query ? `?${query}` : ''
}

export const usageStatsApi = {
  list: (params: UsageStatListParams = {}) =>
    usageRequest<UsageStatListResponse>(`/usage-stats${buildListQuery(params)}`),

  listAll: async (params: Omit<UsageStatListParams, 'page' | 'page_size'> = {}) => {
    const pageSize = 200
    const all: UsageStatItem[] = []
    let page = 1
    let total = 0
    let importedAt: string | null = null

    while (true) {
      const data = await usageRequest<UsageStatListResponse>(
        `/usage-stats${buildListQuery({ ...params, page, page_size: pageSize })}`,
        { timeoutMs: USAGE_HEAVY_TIMEOUT_MS }
      )
      importedAt = data.imported_at
      total = data.total
      all.push(...data.items)
      if (all.length >= total || data.items.length === 0) break
      page += 1
    }

    return { items: all, total, imported_at: importedAt }
  },

  distinctValues: (field: string, focusPduOnly = false) => {
    const search = new URLSearchParams()
    appendFocusPduOnly(search, focusPduOnly)
    const q = search.toString()
    return usageRequest<{ values: string[] }>(
      `/usage-stats/distinct/${encodeURIComponent(field)}${q ? `?${q}` : ''}`
    )
  },

  importExcel: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return usageRequest<UsageStatImportResponse>('/usage-stats/import', {
      method: 'POST',
      body: form,
      timeoutMs: USAGE_HEAVY_TIMEOUT_MS
    })
  },

  downloadTemplate: () =>
    downloadBlob('/usage-stats/template', 'usage_stats_template.xlsx', {
      timeoutMs: USAGE_LIST_TIMEOUT_MS
    }),

  exportExceptions: (failures: UsageImportFailureItem[]) =>
    downloadBlob('/usage-stats/export-exceptions', `usage_import_exceptions_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ failures }),
      timeoutMs: USAGE_LIST_TIMEOUT_MS
    }),

  exportZeroUsage: (deptPath: string[] = []) =>
    downloadBlob('/usage-stats/export-zero-usage', `usage_zero_users_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dept_path: deptPath }),
      timeoutMs: USAGE_HEAVY_TIMEOUT_MS
    })
}
