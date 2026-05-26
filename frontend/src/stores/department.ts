import { defineStore } from 'pinia'
import { ref } from 'vue'
import { departmentApi } from '@/api/department'
import type { DepartmentNode, RootStatus } from '@/types'

export const useDepartmentStore = defineStore('department', () => {
  const tree = ref<DepartmentNode[]>([])
  const rootStatus = ref<RootStatus>({ has_root: false })
  const loading = ref(false)

  const fetchTree = async () => {
    loading.value = true
    try {
      const [status, treeData] = await Promise.all([
        departmentApi.getRootStatus(),
        departmentApi.getTree()
      ])
      rootStatus.value = status
      tree.value = treeData
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
      await fetchTree()
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
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  const updateDepartment = async (deptCode: string, name: string) => {
    loading.value = true
    try {
      await departmentApi.update(deptCode, { name })
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  const deleteDepartment = async (deptCode: string) => {
    loading.value = true
    try {
      await departmentApi.remove(deptCode)
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  return {
    tree,
    rootStatus,
    loading,
    fetchTree,
    createDepartment,
    createDepartmentsBatch,
    updateDepartment,
    deleteDepartment
  }
})
