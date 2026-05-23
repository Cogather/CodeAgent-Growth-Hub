import type {
  NetworkZone,
  ZonePermissionBatchResponse,
  ZonePermissionItem,
  ZonePermissionListResponse,
  ZonePermissionUpdatePayload
} from '@/types'

const BASE = '/api'

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (res.status === 204) return undefined as T
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : `请求失败 (${res.status})`)
  }
  return data as T
}

export const zonePermissionApi = {
  list: (zone: NetworkZone) => requestJson<ZonePermissionListResponse>(`/zone-permissions/${zone}`),

  batchUpsert: (zone: NetworkZone, empNosText: string, modelsText: string) =>
    requestJson<ZonePermissionBatchResponse>(`/zone-permissions/${zone}/batch`, {
      method: 'POST',
      body: JSON.stringify({ emp_nos_text: empNosText, models_text: modelsText })
    }),

  update: (zone: NetworkZone, empNo: string, payload: ZonePermissionUpdatePayload) =>
    requestJson<ZonePermissionItem>(`/zone-permissions/${zone}/${encodeURIComponent(empNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),

  remove: (zone: NetworkZone, empNo: string) =>
    requestJson<void>(`/zone-permissions/${zone}/${encodeURIComponent(empNo)}`, { method: 'DELETE' })
}
