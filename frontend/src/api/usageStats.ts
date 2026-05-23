import { downloadBlob, requestJson } from '@/api/client'
import type {
  UsageImportFailureItem,
  UsageStatImportResponse,
  UsageStatListResponse
} from '@/types'

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
    }),

  exportZeroUsage: (deptPath: string[] = []) =>
    downloadBlob('/usage-stats/export-zero-usage', `usage_zero_users_${new Date().toISOString().slice(0, 10)}.xlsx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dept_path: deptPath })
    })
}
