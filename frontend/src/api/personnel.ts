import { downloadBlob, requestJson, type FetchOptions } from '@/api/client'
import type {
  ImportFailureItem,
  PersonnelBatchImportResponse,
  PersonnelItem,
  PersonnelListResponse,
  PersonnelUpdatePayload
} from '@/types'
import { PERSONNEL_IMPORT_CHUNK_TIMEOUT_MS } from '@/utils/personnelImport'

export const personnelApi = {
  list: () => requestJson<PersonnelListResponse>('/personnel'),

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
