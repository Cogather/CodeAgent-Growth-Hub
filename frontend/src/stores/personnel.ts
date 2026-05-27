import { defineStore } from 'pinia'
import { ref } from 'vue'
import { personnelApi } from '@/api/personnel'
import type { ImportFailureItem, PersonnelItem, PersonnelUpdatePayload } from '@/types'

export const usePersonnelStore = defineStore('personnel', () => {
  const items = ref<PersonnelItem[]>([])
  const loading = ref(false)

  const fetchList = async () => {
    loading.value = true
    try {
      const data = await personnelApi.list()
      items.value = data.items
    } finally {
      loading.value = false
    }
  }

  const batchImport = async (empNosText: string) => {
    loading.value = true
    try {
      const result = await personnelApi.batchImport(empNosText)
      await fetchList()
      if (result.failures.length > 0) {
        await personnelApi.exportExceptions(result.failures)
      }
      return result
    } finally {
      loading.value = false
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
    fetchList,
    batchImport,
    updatePersonnel,
    deletePersonnel,
    exportExceptions
  }
})
