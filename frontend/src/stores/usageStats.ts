import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usageStatsApi } from '@/api/usageStats'
import type { UsageImportFailureItem, UsageStatItem, UsageStatListParams } from '@/types'

export type UsageFilters = Pick<
  UsageStatListParams,
  'q' | 'dept_l3_name' | 'dept_l4_name' | 'dept_l5_name' | 'dept_l6_name'
>

export const useUsageStatsStore = defineStore('usageStats', () => {
  const items = ref<UsageStatItem[]>([])
  const total = ref(0)
  const totalAll = ref(0)
  const page = ref(1)
  const pageSize = ref(50)
  const filters = ref<UsageFilters>({})
  const importedAt = ref<string | null>(null)
  const loading = ref(false)

  async function fetchList(opts?: { page?: number; resetPage?: boolean }) {
    if (opts?.resetPage) page.value = 1
    if (opts?.page !== undefined) page.value = opts.page

    loading.value = true
    try {
      const data = await usageStatsApi.list({
        page: page.value,
        page_size: pageSize.value,
        ...filters.value
      })
      items.value = data.items
      total.value = data.total
      totalAll.value = data.total_all
      page.value = data.page
      pageSize.value = data.page_size
      importedAt.value = data.imported_at
    } finally {
      loading.value = false
    }
  }

  async function setFilters(next: UsageFilters) {
    filters.value = { ...next }
    await fetchList({ resetPage: true })
  }

  async function setPage(nextPage: number) {
    await fetchList({ page: nextPage })
  }

  async function setPageSize(nextPageSize: number) {
    pageSize.value = nextPageSize
    await fetchList({ resetPage: true })
  }

  async function fetchAllItems(params: UsageFilters = {}) {
    const data = await usageStatsApi.listAll(params)
    importedAt.value = data.imported_at
    return data.items
  }

  async function importExcel(file: File) {
    loading.value = true
    try {
      const result = await usageStatsApi.importExcel(file)
      await fetchList({ resetPage: true })
      return result
    } finally {
      loading.value = false
    }
  }

  async function downloadTemplate() {
    await usageStatsApi.downloadTemplate()
  }

  async function exportExceptions(failures: UsageImportFailureItem[]) {
    await usageStatsApi.exportExceptions(failures)
  }

  async function exportZeroUsage(deptPath: string[] = []) {
    await usageStatsApi.exportZeroUsage(deptPath)
  }

  return {
    items,
    total,
    totalAll,
    page,
    pageSize,
    filters,
    importedAt,
    loading,
    fetchList,
    setFilters,
    setPage,
    setPageSize,
    fetchAllItems,
    importExcel,
    downloadTemplate,
    exportExceptions,
    exportZeroUsage
  }
})
