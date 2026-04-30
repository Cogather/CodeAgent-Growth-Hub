<template>
  <div class="system-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
          <el-button type="primary" @click="exportLogs">导出</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="操作人">
          <el-input v-model="queryForm.operator" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="queryForm.action" placeholder="请选择" clearable>
            <el-option label="导出" value="export" />
            <el-option label="审批" value="approve" />
            <el-option label="状态变更" value="status_change" />
            <el-option label="登录" value="login" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="queryForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="logs" style="width: 100%">
        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getActionName(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operatorName" label="操作人" width="120" />
        <el-table-column prop="target" label="操作对象" min-width="200" />
        <el-table-column prop="detail" label="详情" min-width="250" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="操作时间" width="180" />
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const queryForm = reactive({
  operator: '',
  action: '',
  dateRange: [] as Date[]
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(50)

const logs = ref([
  { id: 1, action: 'export', operator: 'admin', operatorName: '管理员', target: '问题单列表', detail: '导出了 50 条数据', createdAt: '2026-04-02 14:30:00' },
  { id: 2, action: 'approve', operator: 'admin', operatorName: '管理员', target: 'AF-20260402-0001', detail: '审批通过', createdAt: '2026-04-02 14:00:00' },
  { id: 3, action: 'status_change', operator: 'admin', operatorName: '管理员', target: 'AF-20260402-0001', detail: '状态变更为处理中', createdAt: '2026-04-02 13:00:00' },
  { id: 4, action: 'export', operator: 'admin', operatorName: '管理员', target: '用户使用数据', detail: '导出了黄区数据', createdAt: '2026-04-02 11:00:00' },
  { id: 5, action: 'login', operator: '10001', operatorName: '张三', target: '系统登录', detail: '用户登录成功', createdAt: '2026-04-02 10:00:00' }
])

const getActionName = (action: string) => {
  const map: Record<string, string> = {
    export: '导出',
    approve: '审批',
    status_change: '状态变更',
    login: '登录'
  }
  return map[action] || action
}

const loadData = () => {}
const resetQuery = () => {
  queryForm.operator = ''
  queryForm.action = ''
  queryForm.dateRange = []
}

const exportLogs = () => {
  ElMessage.success('导出成功')
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
</style>
