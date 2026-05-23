import { requestJson } from '@/api/client'
import type {
  NetworkZone,
  ZonePermissionBatchResponse,
  ZonePermissionItem,
  ZonePermissionListResponse,
  ZonePermissionUpdatePayload
} from '@/types'

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
