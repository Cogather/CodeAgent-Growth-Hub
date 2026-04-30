<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="page-title">
        <h2>仪表盘</h2>
        <p>欢迎回来，{{ authStore.user?.name }}</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-card card-pending">
          <div class="stat-bg"></div>
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ pendingRequests }}</div>
              <div class="stat-label">待处理申请</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card card-completed">
          <div class="stat-bg"></div>
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ completedRequests }}</div>
              <div class="stat-label">已完成申请</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card card-users">
          <div class="stat-bg"></div>
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalUsers }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card card-artifacts">
          <div class="stat-bg"></div>
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="24"><Collection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalArtifacts }}</div>
              <div class="stat-label">产出数量</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>各区域使用量分布</span>
              <el-tag type="warning" effect="plain" size="small">实时</el-tag>
            </div>
          </template>
          <div ref="zoneChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>申请趋势</span>
              <el-tag type="success" effect="plain" size="small">近7天</el-tag>
            </div>
          </template>
          <div ref="trendChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Document /></el-icon>
                最近申请
              </span>
              <el-button type="primary" link @click="$router.push('/permission/my-requests')">
                查看更多 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentRequests" style="width: 100%">
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
            <el-table-column prop="createdAt" label="提交时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { useMockDataStore } from '@/stores/mockData'
import { useAuthStore } from '@/stores/auth'
import type { ZoneType } from '@/types'

const mockDataStore = useMockDataStore()
const authStore = useAuthStore()

const zoneChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

const pendingRequests = computed(() => 
  mockDataStore.accessRequests.filter(r => r.status === 'pending' || r.status === 'processing').length
)
const completedRequests = computed(() => 
  mockDataStore.accessRequests.filter(r => r.status === 'completed').length
)
const totalUsers = computed(() => mockDataStore.usageStats.length)
const totalArtifacts = computed(() => mockDataStore.artifacts.length)

const recentRequests = computed(() => mockDataStore.accessRequests.slice(0, 5))

const getZoneType = (zone: ZoneType) => {
  const map: Record<ZoneType, 'warning' | 'primary' | 'success'> = {
    yellow: 'warning',
    blue: 'primary',
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
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'warning',
    processing: 'info',
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

onMounted(() => {
  if (zoneChartRef.value) {
    const zoneChart = echarts.init(zoneChartRef.value)
    const zoneData = mockDataStore.usageStats.reduce((acc, stat) => {
      acc[stat.zone] = (acc[stat.zone] || 0) + stat.callCount
      return acc
    }, {} as Record<string, number>)
    
    zoneChart.setOption({
      tooltip: { 
        trigger: 'item',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e5e7eb',
        textStyle: { color: '#374151' }
      },
      legend: { bottom: '5%', left: 'center', itemGap: 20 },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { 
          borderRadius: 8, 
          borderColor: '#fff', 
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        },
        label: { show: false },
        emphasis: { 
          label: { show: true, fontSize: 14, fontWeight: '600' },
          itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.2)' }
        },
        data: [
          { value: zoneData.yellow || 0, name: '黄区', itemStyle: { color: '#f59e0b' } },
          { value: zoneData.blue || 0, name: '蓝区', itemStyle: { color: '#3b82f6' } },
          { value: zoneData.green || 0, name: '绿区', itemStyle: { color: '#10b981' } }
        ]
      }]
    })
  }

  if (trendChartRef.value) {
    const trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { 
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e5e7eb',
        textStyle: { color: '#374151' }
      },
      legend: { data: ['申请数', '完成数'], bottom: '0%', itemGap: 20 },
      grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
      xAxis: { 
        type: 'category', 
        data: ['04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07'],
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#6b7280' }
      },
      yAxis: { 
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
        axisLabel: { color: '#6b7280' }
      },
      series: [
        { 
          name: '申请数', 
          type: 'line', 
          data: [12, 15, 18, 20, 22, 25, 28], 
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#6366f1' },
          itemStyle: { color: '#6366f1' },
          areaStyle: { color: 'rgba(99, 102, 241, 0.15)' }
        },
        { 
          name: '完成数', 
          type: 'line', 
          data: [10, 12, 14, 16, 19, 22, 25], 
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#10b981' },
          itemStyle: { color: '#10b981' },
          areaStyle: { color: 'rgba(16, 185, 129, 0.15)' }
        }
      ]
    })
  }
})
</script>

<style scoped>
.dashboard {
  padding: 0;
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

.stat-card {
  position: relative;
  border: none;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-card .stat-bg {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  opacity: 0.15;
}

.card-pending .stat-bg {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.card-completed .stat-bg {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.card-users .stat-bg {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.card-artifacts .stat-bg {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-pending .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.card-completed .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.card-users .stat-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.card-artifacts .stat-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.chart-card {
  border: none;
  border-radius: 16px;
}

.chart-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.chart-card :deep(.el-card__body) {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
  color: #1f2937;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-card {
  border: none;
  border-radius: 16px;
}

.table-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.table-card :deep(.el-card__body) {
  padding: 0;
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
