import { defineStore } from 'pinia'
import { ref } from 'vue'
import { personnelApi } from '@/api/personnel'
import type { ImportFailureItem, PersonnelItem, PersonnelListParams, PersonnelUpdatePayload } from '@/types'
import {
  chunkEmpNos,
  parseEmpNos,
  type PersonnelImportProgress,
  type PersonnelImportResult
} from '@/utils/personnelImport'

export type PersonnelFilters = Pick<
  PersonnelListParams,
  'q' | 'dept_l3_name' | 'dept_l4_name' | 'dept_l5_name' | 'dept_l6_name'
>

export const usePersonnelStore = defineStore('personnel', () => {
  const items = ref<PersonnelItem[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(50)
  const filters = ref<PersonnelFilters>({})
  const loading = ref(false)
  const importing = ref(false)

  const fetchList = async (opts?: { page?: number; resetPage?: boolean }) => {
    if (opts?.resetPage) {
      page.value = 1
    }
    if (opts?.page !== undefined) {
      page.value = opts.page
    }

    loading.value = true
    try {
      const data = await personnelApi.list({
        page: page.value,
        page_size: pageSize.value,
        ...filters.value
      })
      items.value = data.items
      total.value = data.total
      page.value = data.page
      pageSize.value = data.page_size
    } finally {
      loading.value = false
    }
  }

  const setFilters = async (next: PersonnelFilters) => {
    filters.value = { ...next }
    await fetchList({ resetPage: true })
  }

  const setPage = async (nextPage: number) => {
    await fetchList({ page: nextPage })
  }

  const setPageSize = async (nextPageSize: number) => {
    pageSize.value = nextPageSize
    await fetchList({ resetPage: true })
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

      await fetchList({ resetPage: true })

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
      if (items.value.length === 1 && page.value > 1) {
        await fetchList({ page: page.value - 1 })
      } else {
        await fetchList()
      }
    } finally {
      loading.value = false
    }
  }

  const exportExceptions = async (failures: ImportFailureItem[]) => {
    await personnelApi.exportExceptions(failures)
  }

  return {
    items,
    total,
    page,
    pageSize,
    filters,
    loading,
    importing,
    fetchList,
    setFilters,
    setPage,
    setPageSize,
    batchImport,
    updatePersonnel,
    deletePersonnel,
    exportExceptions
  }
})
