import { defineStore } from 'pinia'
import { ref } from 'vue'
import { departmentApi } from '@/api/department'
import type { RootStatus } from '@/types'

export const useDepartmentStore = defineStore('department', () => {
  const rootStatus = ref<RootStatus>({ has_root: false })
  const loading = ref(false)

  const fetchRootStatus = async () => {
    rootStatus.value = await departmentApi.getRootStatus()
  }

  const refreshStatus = async () => {
    loading.value = true
    try {
      await fetchRootStatus()
    } finally {
      loading.value = false
    }
  }

  const createDepartment = async (
    parentDeptCode: string | null,
    deptCode: string,
    name: string
  ) => {
    loading.value = true
    try {
      await departmentApi.create({
        dept_code: deptCode,
        parent_dept_code: parentDeptCode,
        name
      })
      await fetchRootStatus()
    } finally {
      loading.value = false
    }
  }

  const createDepartmentsBatch = async (
    parentDeptCode: string,
    items: { name: string; dept_code: string }[]
  ) => {
    if (items.length === 0) return
    loading.value = true
    try {
      for (const item of items) {
        await departmentApi.create({
          dept_code: item.dept_code,
          parent_dept_code: parentDeptCode,
          name: item.name
        })
      }
      await fetchRootStatus()
    } finally {
      loading.value = false
    }
  }

  const updateDepartment = async (deptCode: string, name: string) => {
    loading.value = true
    try {
      await departmentApi.update(deptCode, { name })
    } finally {
      loading.value = false
    }
  }

  const deleteDepartment = async (deptCode: string) => {
    loading.value = true
    try {
      await departmentApi.remove(deptCode)
      await fetchRootStatus()
    } finally {
      loading.value = false
    }
  }

  return {
    rootStatus,
    loading,
    fetchRootStatus,
    refreshStatus,
    createDepartment,
    createDepartmentsBatch,
    updateDepartment,
    deleteDepartment
  }
})
