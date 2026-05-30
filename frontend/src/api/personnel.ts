import { downloadBlob, requestJson, type FetchOptions } from '@/api/client'
import type {
  ImportFailureItem,
  PersonnelBatchImportResponse,
  PersonnelDistinctResponse,
  PersonnelItem,
  PersonnelListParams,
  PersonnelListResponse,
  PersonnelUpdatePayload
} from '@/types'
import { PERSONNEL_IMPORT_CHUNK_TIMEOUT_MS } from '@/utils/personnelImport'

const buildListQuery = (params: PersonnelListParams = {}) => {
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

export const personnelApi = {
  list: (params: PersonnelListParams = {}) =>
    requestJson<PersonnelListResponse>(`/personnel${buildListQuery(params)}`),

  listAll: async (params: Omit<PersonnelListParams, 'page' | 'page_size'> = {}) => {
    const pageSize = 200
    const all: PersonnelItem[] = []
    let page = 1
    let total = 0
    const listTimeoutMs = 120_000

    while (true) {
      const data = await requestJson<PersonnelListResponse>(`/personnel${buildListQuery({ ...params, page, page_size: pageSize })}`, {
        timeoutMs: listTimeoutMs
      })
      total = data.total
      all.push(...data.items)
      if (all.length >= total || data.items.length === 0) break
      page += 1
    }

    return { items: all, total }
  },

  distinctValues: (field: string) =>
    requestJson<PersonnelDistinctResponse>(`/personnel/distinct/${encodeURIComponent(field)}`),

  batchImport: (empNosText: string, options?: FetchOptions) =>
    requestJson<PersonnelBatchImportResponse>('/personnel/batch-import', {
      method: 'POST',
      body: JSON.stringify({ emp_nos_text: empNosText }),
      timeoutMs: PERSONNEL_IMPORT_CHUNK_TIMEOUT_MS,
      ...options
    }),

  update: (empNo: string, payload: PersonnelUpdatePayload) =>
    requestJson<PersonnelItem>(`/personnel/${encodeURIComponent(empNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),

  remove: (empNo: string) =>
    requestJson<void>(`/personnel/${encodeURIComponent(empNo)}`, { method: 'DELETE' }),

  exportExceptions: async (failures: ImportFailureItem[]) => {
    await downloadBlob('/personnel/export-exceptions', `personnel_import_exceptions_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ failures })
    })
  }
}
