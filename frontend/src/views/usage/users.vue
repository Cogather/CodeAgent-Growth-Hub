<template>
  <div class="users-page">
    <div class="page-header">
      <div class="page-title">
        <h2>人员明细</h2>
        <p>查看各区域用户使用数据明细</p>
      </div>
      <div class="page-action">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <el-tabs v-model="activeZone" class="zone-tabs">
        <el-tab-pane label="黄区" name="yellow" />
        <el-tab-pane label="蓝区" name="blue" />
        <el-tab-pane label="绿区" name="green" />
      </el-tabs>
      
      <div class="filters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="工具">
            <el-select v-model="filters.tool" placeholder="请选择" clearable style="width: 140px">
              <el-option v-for="t in tools" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="filters.department" placeholder="请选择" clearable style="width: 160px">
              <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.name" />
            </el-select>
          </el-form-item>
          <el-form-item label="深度用户">
            <el-select v-model="filters.isDeepUser" placeholder="请选择" clearable style="width: 140px">
              <el-option label="是" :value="true" />
              <el-option label="否" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="filteredUsers" style="width: 100%">
        <el-table-column prop="username" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="150" />
        <el-table-column prop="tool" label="工具" width="120" />
        <el-table-column prop="callCount" label="累计调用量" width="120" sortable />
        <el-table-column prop="activeDays" label="累计使用天数" width="130" sortable />
        <el-table-column prop="isDeepUser" label="是否深度用户" width="120">
          <template #default="{ row }">
            <el-tag :type="row.isDeepUser ? 'success' : 'info'" effect="plain">
              {{ row.isDeepUser ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'
import type { ZoneType } from '@/types'

const mockDataStore = useMockDataStore()

const activeZone = ref<ZoneType>('yellow')
const filters = reactive({
  tool: '',
  department: '',
  isDeepUser: null as boolean | null
})

const tools = computed(() => mockDataStore.tools)
const departments = computed(() => mockDataStore.departments)

const filteredUsers = computed(() => {
  let list = mockDataStore.usageStats.filter(s => s.zone === activeZone.value)
  if (filters.tool) {
    list = list.filter(s => s.tool === filters.tool)
  }
  if (filters.department) {
    list = list.filter(s => s.department === filters.department)
  }
  if (filters.isDeepUser !== null) {
    list = list.filter(s => s.isDeepUser === filters.isDeepUser)
  }
  return list
})

const loadData = () => {}
const resetFilters = () => {
  filters.tool = ''
  filters.department = ''
  filters.isDeepUser = null
}

const exportData = () => {
  ElMessage.success('导出成功')
}
</script>

<style scoped>
.users-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.table-card {
  border: none;
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 20px;
}

.zone-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.zone-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

.zone-tabs :deep(.el-tabs__item.is-active) {
  color: #6366f1;
}

.zone-tabs :deep(.el-tabs__active-bar) {
  background-color: #6366f1;
}

.filters {
  margin-bottom: 20px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-table) {
  --el-table-border-color: #f3f4f6;
  --el-table-header-bg-color: #fafbfc;
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
  color: #374151;
}

:deep(.el-table td.el-table__cell) {
  font-size: 13px;
}
</style>
