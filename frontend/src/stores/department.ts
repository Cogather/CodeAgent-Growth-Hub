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

  const createDepartment = async (parentId: number | null, name: string) => {
    loading.value = true
    try {
      await departmentApi.create({ parent_id: parentId, name })
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  const createDepartmentsBatch = async (parentId: number, names: string[]) => {
    if (names.length === 0) return
    loading.value = true
    try {
      for (const name of names) {
        await departmentApi.create({ parent_id: parentId, name })
      }
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  const updateDepartment = async (id: number, name: string) => {
    loading.value = true
    try {
      await departmentApi.update(id, { name })
      await fetchTree()
    } finally {
      loading.value = false
    }
  }

  const deleteDepartment = async (id: number) => {
    loading.value = true
    try {
      await departmentApi.remove(id)
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
