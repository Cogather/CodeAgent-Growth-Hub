<template>
  <div class="system-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <el-button type="primary" @click="showAddDialog">新增部门</el-button>
        </div>
      </template>
      
      <el-tree :data="treeData" :props="treeProps" default-expand-all>
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span>{{ node.label }}</span>
            <span>
              <el-button type="primary" link size="small" @click="appendNode(data)">添加子部门</el-button>
              <el-button type="danger" link size="small" @click="removeNode(node, data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'

const mockDataStore = useMockDataStore()

const treeProps = {
  children: 'children',
  label: 'name'
}

const treeData = computed(() => {
  const depts = mockDataStore.departments
  const buildTree = (parentId: number | null): any[] => {
    return depts
      .filter(d => d.parentId === parentId)
      .map(d => ({
        ...d,
        children: buildTree(d.id)
      }))
  }
  return buildTree(null)
})

const showAddDialog = () => {
  ElMessage.info('功能开发中')
}

const appendNode = (data: any) => {
  ElMessage.info('功能开发中')
}

const removeNode = async (node: any, data: any) => {
  await ElMessageBox.confirm('确定要删除该部门吗?', '提示', { type: 'warning' })
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.system-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.custom-tree-node {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
</style>
