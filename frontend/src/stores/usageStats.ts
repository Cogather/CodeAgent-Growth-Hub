import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usageStatsApi } from '@/api/usageStats'
import type { UsageImportFailureItem, UsageStatItem } from '@/types'

export const useUsageStatsStore = defineStore('usageStats', () => {
  const items = ref<UsageStatItem[]>([])
  const importedAt = ref<string | null>(null)
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try {
      const data = await usageStatsApi.list()
      items.value = data.items
      importedAt.value = data.imported_at
    } finally {
      loading.value = false
    }
  }

  async function importExcel(file: File) {
    loading.value = true
    try {
      const result = await usageStatsApi.importExcel(file)
      await fetchList()
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

  return {
    items,
    importedAt,
    loading,
    fetchList,
    importExcel,
    downloadTemplate,
    exportExceptions
  }
})
