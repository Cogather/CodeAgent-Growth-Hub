<template>
  <div class="tickets-page">
    <div class="page-header">
      <div class="page-title">
        <h2>12345服务单分析</h2>
        <p>查看和分析所有问题单处理情况</p>
      </div>
      <div class="page-action">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="filters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="部门">
            <el-select v-model="queryForm.department" placeholder="请选择" clearable style="width: 160px">
              <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.name" />
            </el-select>
          </el-form-item>
          <el-form-item label="类别">
            <el-select v-model="queryForm.category" placeholder="请选择" clearable style="width: 140px">
              <el-option label="Bug" value="bug" />
              <el-option label="功能需求" value="feature" />
              <el-option label="问题咨询" value="question" />
              <el-option label="优化建议" value="optimization" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" placeholder="请选择" clearable style="width: 140px">
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetQuery">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="filteredTickets" style="width: 100%">
        <el-table-column prop="ticketNo" label="单号" width="150" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag effect="light">{{ getCategoryName(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitterName" label="提交人" width="100" />
        <el-table-column prop="processorName" label="处理人" width="100">
          <template #default="{ row }">
            {{ row.processorName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="createdAt" label="提交时间" width="180" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" link :href="row.link" target="_blank">链接</el-button>
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
import type { Ticket, TicketCategory, TicketStatus } from '@/types'

const mockDataStore = useMockDataStore()

const queryForm = reactive({
  department: '',
  category: '' as TicketCategory | '',
  status: '' as TicketStatus | ''
})

const departments = computed(() => mockDataStore.departments)

const filteredTickets = computed(() => {
  let list = mockDataStore.tickets
  if (queryForm.department) {
    list = list.filter(t => t.department === queryForm.department)
  }
  if (queryForm.category) {
    list = list.filter(t => t.category === queryForm.category)
  }
  if (queryForm.status) {
    list = list.filter(t => t.status === queryForm.status)
  }
  return list
})

const getCategoryName = (category: TicketCategory) => {
  const map: Record<TicketCategory, string> = {
    bug: 'Bug',
    feature: '功能需求',
    question: '问题咨询',
    optimization: '优化建议'
  }
  return map[category]
}

const getStatusType = (status: TicketStatus) => {
  const map: Record<TicketStatus, 'success' | 'warning' | 'danger'> = {
    pending: 'warning',
    processing: 'warning',
    resolved: 'success',
    closed: 'warning'
  }
  return map[status]
}

const getStatusName = (status: TicketStatus) => {
  const map: Record<TicketStatus, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return map[status]
}

const loadData = () => {}
const resetQuery = () => {
  queryForm.department = ''
  queryForm.category = ''
  queryForm.status = ''
}

const exportData = () => {
  ElMessage.success('导出成功')
}
</script>

<style scoped>
.tickets-page {
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
