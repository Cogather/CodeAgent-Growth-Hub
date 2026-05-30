import { downloadBlob, requestJson, type FetchOptions } from '@/api/client'
import type {
  NetworkZone,
  PersonnelDistinctResponse,
  ZoneEmpNosResponse,
  ZoneImportFailureItem,
  ZonePermissionBatchResponse,
  ZonePermissionItem,
  ZonePermissionListParams,
  ZonePermissionListResponse,
  ZonePermissionUpdatePayload
} from '@/types'

const ZONE_REQUEST_TIMEOUT_MS = 60_000

const buildListQuery = (params: ZonePermissionListParams = {}) => {
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

const zoneFetch = <T>(url: string, options?: FetchOptions) =>
  requestJson<T>(url, { timeoutMs: ZONE_REQUEST_TIMEOUT_MS, ...options })

export const zonePermissionApi = {
  list: (zone: NetworkZone, params: ZonePermissionListParams = {}) =>
    zoneFetch<ZonePermissionListResponse>(`/zone-permissions/${zone}${buildListQuery(params)}`),

  listEmpNos: (zone: NetworkZone) =>
    zoneFetch<ZoneEmpNosResponse>(`/zone-permissions/${zone}/emp-nos`),

  distinctValues: (zone: NetworkZone, field: string) =>
    zoneFetch<PersonnelDistinctResponse>(
      `/zone-permissions/${zone}/distinct/${encodeURIComponent(field)}`
    ),

  batchUpsert: (zone: NetworkZone, empNosText: string, modelsText: string) =>
    zoneFetch<ZonePermissionBatchResponse>(`/zone-permissions/${zone}/batch`, {
      method: 'POST',
      body: JSON.stringify({ emp_nos_text: empNosText, models_text: modelsText })
    }),

  update: (zone: NetworkZone, empNo: string, payload: ZonePermissionUpdatePayload) =>
    zoneFetch<ZonePermissionItem>(`/zone-permissions/${zone}/${encodeURIComponent(empNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),

  remove: (zone: NetworkZone, empNo: string) =>
    zoneFetch<void>(`/zone-permissions/${zone}/${encodeURIComponent(empNo)}`, { method: 'DELETE' }),

  exportExceptions: async (zone: NetworkZone, failures: ZoneImportFailureItem[]) => {
    await downloadBlob(
      `/zone-permissions/${zone}/export-exceptions`,
      `zone_${zone}_import_exceptions_${new Date().toISOString().slice(0, 10)}.xlsx`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ failures }),
        timeoutMs: ZONE_REQUEST_TIMEOUT_MS
      }
    )
  }
}
