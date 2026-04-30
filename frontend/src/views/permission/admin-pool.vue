<template>
  <div class="admin-pool-page">
    <div class="page-header">
      <div class="page-title">
        <h2>管理员处理池</h2>
        <p>处理所有权限申请，批量审批与管理</p>
      </div>
      <div class="page-action">
        <el-statistic title="处理进度">
          <template #suffix>
            <span>/ {{ mockDataStore.accessRequests.length }}</span>
          </template>
          {{ completedCount }}
        </el-statistic>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <div class="filters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="区域">
            <el-select v-model="queryForm.zone" placeholder="请选择" clearable style="width: 120px">
              <el-option label="黄区" value="yellow" />
              <el-option label="蓝区" value="blue" />
              <el-option label="绿区" value="green" />
            </el-select>
          </el-form-item>
          <el-form-item label="工具">
            <el-select v-model="queryForm.tool" placeholder="请选择" clearable style="width: 140px">
              <el-option v-for="t in mockDataStore.tools" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryForm.status" placeholder="请选择" clearable style="width: 140px">
              <el-option label="待受理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
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
      
      <div class="table-toolbar">
        <el-button type="primary" :disabled="selectedRows.length === 0" @click="batchProcess">
          <el-icon><Check /></el-icon>
          批量处理
        </el-button>
        <el-button type="success" :disabled="selectedRows.length === 0" @click="batchComplete">
          <el-icon><CircleCheck /></el-icon>
          批量完成
        </el-button>
        <el-button type="danger" :disabled="selectedRows.length === 0" @click="batchReject">
          <el-icon><CircleClose /></el-icon>
          批量驳回
        </el-button>
      </div>
      
      <el-table
        ref="tableRef"
        :data="filteredRequests"
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
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
        <el-table-column prop="submitterName" label="提交人" width="100" />
        <el-table-column prop="accounts" label="工号数" width="80">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ row.accounts.length }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button type="success" link @click="processOne(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="detailVisible" title="电子流详情" width="700px" class="detail-dialog">
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
      </el-descriptions>
      
      <el-table :data="currentRequest?.accounts" style="margin-top: 16px" size="small">
        <el-table-column prop="username" label="工号" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <div class="dialog-footer">
          <el-input
            v-model="processRemark"
            type="textarea"
            :rows="3"
            placeholder="请输入处理备注"
            style="margin-bottom: 16px; width: 100%"
          />
          <el-button @click="detailVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmProcess">确认处理</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'
import type { AccessRequest, ZoneType, RequestStatus } from '@/types'

const mockDataStore = useMockDataStore()

const queryForm = reactive({
  zone: '',
  tool: '',
  status: ''
})

const tableRef = ref()
const selectedRows = ref<AccessRequest[]>([])
const detailVisible = ref(false)
const currentRequest = ref<AccessRequest | null>(null)
const processRemark = ref('')

const completedCount = computed(() => 
  mockDataStore.accessRequests.filter(r => r.status === 'completed').length
)

const filteredRequests = computed(() => {
  let list = mockDataStore.accessRequests
  if (queryForm.zone) {
    list = list.filter(r => r.zone === queryForm.zone)
  }
  if (queryForm.tool) {
    list = list.filter(r => r.tool === queryForm.tool)
  }
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

const handleSelectionChange = (rows: AccessRequest[]) => {
  selectedRows.value = rows
}

const loadData = () => {}
const resetQuery = () => {
  queryForm.zone = ''
  queryForm.tool = ''
  queryForm.status = ''
}

const showDetail = (row: AccessRequest) => {
  currentRequest.value = row
  processRemark.value = ''
  detailVisible.value = true
}

const processOne = (row: AccessRequest) => {
  mockDataStore.updateAccessRequestStatus(row.id, 'processing')
  ElMessage.success('已设置为处理中')
}

const confirmProcess = () => {
  if (currentRequest.value) {
    mockDataStore.updateAccessRequestStatus(currentRequest.value.id, 'processing', processRemark.value)
    ElMessage.success('处理成功')
    detailVisible.value = false
  }
}

const batchProcess = async () => {
  await ElMessageBox.confirm(`确定要批量处理选中的 ${selectedRows.value.length} 条申请吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  
  selectedRows.value.forEach(row => {
    mockDataStore.updateAccessRequestStatus(row.id, 'processing')
  })
  ElMessage.success('批量处理成功')
  tableRef.value?.clearSelection()
}

const batchComplete = async () => {
  await ElMessageBox.confirm(`确定要批量完成选中的 ${selectedRows.value.length} 条申请吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'success'
  })
  
  selectedRows.value.forEach(row => {
    mockDataStore.updateAccessRequestStatus(row.id, 'completed')
  })
  ElMessage.success('批量完成')
  tableRef.value?.clearSelection()
}

const batchReject = async () => {
  await ElMessageBox.confirm(`确定要批量驳回选中的 ${selectedRows.value.length} 条申请吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  })
  
  selectedRows.value.forEach(row => {
    mockDataStore.updateAccessRequestStatus(row.id, 'rejected')
  })
  ElMessage.success('批量驳回')
  tableRef.value?.clearSelection()
}
</script>

<style scoped>
.admin-pool-page {
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

.page-action :deep(.el-statistic__content) {
  font-size: 28px;
  font-weight: 700;
  color: #6366f1;
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

.table-toolbar {
  margin: 16px 0;
  display: flex;
  gap: 12px;
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

.dialog-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
