import { requestJson, type FetchOptions } from '@/api/client'
import type {
  NetworkZone,
  ZonePermissionBatchResponse,
  ZonePermissionItem,
  ZonePermissionListResponse,
  ZonePermissionUpdatePayload
} from '@/types'

const ZONE_REQUEST_TIMEOUT_MS = 60_000

const zoneFetch = <T>(url: string, options?: FetchOptions) =>
  requestJson<T>(url, { timeoutMs: ZONE_REQUEST_TIMEOUT_MS, ...options })

export const zonePermissionApi = {
  list: (zone: NetworkZone) => zoneFetch<ZonePermissionListResponse>(`/zone-permissions/${zone}`),

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
    zoneFetch<void>(`/zone-permissions/${zone}/${encodeURIComponent(empNo)}`, { method: 'DELETE' })
}
