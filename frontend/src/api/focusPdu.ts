import { requestJson } from '@/api/client'
import type { FocusPduCreatePayload, FocusPduListResponse } from '@/types'

export const focusPduApi = {
  list: () => requestJson<FocusPduListResponse>('/focus-pdus'),

  listCandidates: () => requestJson<FocusPduListResponse>('/focus-pdus/candidates'),

  add: (payload: FocusPduCreatePayload) =>
    requestJson<FocusPduListResponse['items'][0]>('/focus-pdus', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  remove: (deptCode: string) =>
    requestJson<void>(`/focus-pdus/${encodeURIComponent(deptCode)}`, { method: 'DELETE' })
}
