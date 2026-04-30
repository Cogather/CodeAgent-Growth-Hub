<template>
  <div class="my-requests-page">
    <div class="page-header">
      <div class="page-title">
        <h2>我的电子流</h2>
        <p>查看您提交的所有权限申请记录</p>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="filters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" placeholder="请选择" clearable style="width: 140px">
              <el-option label="待受理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="已驳回" value="rejected" />
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
      
      <el-table :data="filteredRequests" style="width: 100%">
        <el-table-column prop="requestNo" label="单号" width="180" />
        <el-table-column prop="zone" label="区域" width="100">
          <template #default="{ row }">
            <el-tag :type="getZoneType(row.zone)" effect="light">{{ getZoneName(row.zone) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tool" label="工具" width="120" />
        <el-table-column prop="model" label="模型" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="detailVisible" title="电子流详情" width="650px" class="detail-dialog">
      <el-descriptions :column="2" border v-if="currentRequest">
        <el-descriptions-item label="单号">{{ currentRequest.requestNo }}</el-descriptions-item>
        <el-descriptions-item label="区域">
          <el-tag :type="getZoneType(currentRequest.zone)" effect="light">{{ getZoneName(currentRequest.zone) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="工具">{{ currentRequest.tool }}</el-descriptions-item>
        <el-descriptions-item label="模型">{{ currentRequest.model }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRequest.status)" effect="dark">{{ getStatusName(currentRequest.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交人">{{ currentRequest.submitterName }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ currentRequest.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="处理人">{{ currentRequest.processor || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRequest.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useMockDataStore } from '@/stores/mockData'
import { useAuthStore } from '@/stores/auth'
import type { AccessRequest, ZoneType } from '@/types'

const mockDataStore = useMockDataStore()
const authStore = useAuthStore()

const queryForm = reactive({
  status: ''
})

const detailVisible = ref(false)
const currentRequest = ref<AccessRequest | null>(null)

const filteredRequests = computed(() => {
  let list = mockDataStore.accessRequests.filter(r => r.submitter === authStore.user?.username)
  if (queryForm.status) {
    list = list.filter(r => r.status === queryForm.status)
  }
  return list
})

const getZoneType = (zone: ZoneType) => {
  const map: Record<ZoneType, 'success' | 'warning' | 'danger'> = {
    yellow: 'warning',
    blue: 'warning',
    green: 'success'
  }
  return map[zone]
}

const getZoneName = (zone: ZoneType) => {
  const map: Record<ZoneType, string> = {
    yellow: '黄区',
    blue: '蓝区',
    green: '绿区'
  }
  return map[zone]
}

const getStatusType = (status: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger'> = {
    pending: 'warning',
    processing: 'warning',
    completed: 'success',
    rejected: 'danger'
  }
  return map[status] || 'warning'
}

const getStatusName = (status: string) => {
  const map: Record<string, string> = {
    pending: '待受理',
    processing: '处理中',
    completed: '已完成',
    rejected: '已驳回'
  }
  return map[status] || status
}

const loadData = () => {}
const resetQuery = () => {
  queryForm.status = ''
}

const showDetail = (row: AccessRequest) => {
  currentRequest.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.my-requests-page {
  width: 100%;
}

.page-header {
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

.detail-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f3f4f6;
  padding: 16px 20px;
}

.detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
}
</style>
