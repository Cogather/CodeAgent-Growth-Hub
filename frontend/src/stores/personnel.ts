import { defineStore } from 'pinia'
import { ref } from 'vue'
import { personnelApi } from '@/api/personnel'
import type { ImportFailureItem, PersonnelItem, PersonnelUpdatePayload } from '@/types'
import {
  chunkEmpNos,
  parseEmpNos,
  type PersonnelImportProgress,
  type PersonnelImportResult
} from '@/utils/personnelImport'

export const usePersonnelStore = defineStore('personnel', () => {
  const items = ref<PersonnelItem[]>([])
  const loading = ref(false)
  const importing = ref(false)

  const fetchList = async () => {
    loading.value = true
    try {
      const data = await personnelApi.list()
      items.value = data.items
    } finally {
      loading.value = false
    }
  }

  const batchImport = async (
    empNosText: string,
    options?: {
      onProgress?: (progress: PersonnelImportProgress) => void
      signal?: AbortSignal
    }
  ): Promise<PersonnelImportResult> => {
    const empNos = parseEmpNos(empNosText)
    if (empNos.length === 0) {
      return { imported_count: 0, failures: [], cancelled: false }
    }

    importing.value = true
    const chunks = chunkEmpNos(empNos)
    let importedCount = 0
    const failures: ImportFailureItem[] = []
    let processed = 0
    let cancelled = false

    const reportProgress = () => {
      options?.onProgress?.({
        processed,
        total: empNos.length,
        importedCount,
        failureCount: failures.length,
        cancelled
      })
    }

    reportProgress()

    try {
      for (const chunk of chunks) {
        if (options?.signal?.aborted) {
          cancelled = true
          break
        }

        try {
          const result = await personnelApi.batchImport(chunk.join(','), { signal: options?.signal })
          importedCount += result.imported_count
          failures.push(...result.failures)
        } catch (error) {
          if (options?.signal?.aborted) {
            cancelled = true
            break
          }
          throw error
        }

        processed += chunk.length
        reportProgress()
      }

      await fetchList()

      if (failures.length > 0) {
        await personnelApi.exportExceptions(failures)
      }

      return { imported_count: importedCount, failures, cancelled }
    } finally {
      importing.value = false
    }
  }

  const updatePersonnel = async (empNo: string, payload: PersonnelUpdatePayload) => {
    loading.value = true
    try {
      await personnelApi.update(empNo, payload)
      await fetchList()
    } finally {
      loading.value = false
    }
  }

  const deletePersonnel = async (empNo: string) => {
    loading.value = true
    try {
      await personnelApi.remove(empNo)
      await fetchList()
    } finally {
      loading.value = false
    }
  }

  const exportExceptions = async (failures: ImportFailureItem[]) => {
    await personnelApi.exportExceptions(failures)
  }

  return {
    items,
    loading,
    importing,
    fetchList,
    batchImport,
    updatePersonnel,
    deletePersonnel,
    exportExceptions
  }
})
