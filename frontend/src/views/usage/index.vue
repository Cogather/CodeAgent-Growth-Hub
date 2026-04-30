<template>
  <div class="usage-page">
    <div class="page-header">
      <div class="page-title">
        <h2>使用数据看板</h2>
        <p>查看各区域AI工具使用情况与趋势分析</p>
      </div>
    </div>

    <el-card class="zone-card" shadow="never">
      <el-tabs v-model="activeZone" class="zone-tabs">
        <el-tab-pane label="黄区" name="yellow">
          <div class="zone-content">
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
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="filters.dateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    style="width: 240px"
                  />
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
            
            <el-row :gutter="20" class="stat-row">
              <el-col :span="6">
                <div class="stat-item stat-yellow">
                  <div class="stat-icon">
                    <el-icon :size="20"><DataLine /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ zoneStats.totalCallCount.toLocaleString() }}</div>
                    <div class="stat-label">总调用量</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item stat-blue">
                  <div class="stat-icon">
                    <el-icon :size="20"><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ zoneStats.activeUsers }}</div>
                    <div class="stat-label">活跃人数</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item stat-purple">
                  <div class="stat-icon">
                    <el-icon :size="20"><Star /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ zoneStats.deepUsers }}</div>
                    <div class="stat-label">深度用户</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item stat-green">
                  <div class="stat-icon">
                    <el-icon :size="20"><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ zoneStats.avgCallPerUser }}</div>
                    <div class="stat-label">人均调用量</div>
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="chart-card">
                  <div class="chart-title">
                    <el-icon><Histogram /></el-icon>
                    部门调用量TOP10
                  </div>
                  <div ref="deptChartRef" style="height: 300px"></div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="chart-card">
                  <div class="chart-title">
                    <el-icon><TrendCharts /></el-icon>
                    日调用量趋势
                  </div>
                  <div ref="trendChartRef" style="height: 300px"></div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="蓝区" name="blue" />
        <el-tab-pane label="绿区" name="green" />
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, reactive } from 'vue'
import * as echarts from 'echarts'
import { useMockDataStore } from '@/stores/mockData'
import type { ZoneType } from '@/types'

const mockDataStore = useMockDataStore()

const activeZone = ref<ZoneType>('yellow')
const deptChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

const filters = reactive({
  tool: '',
  department: '',
  dateRange: [] as Date[]
})

const tools = computed(() => mockDataStore.tools)
const departments = computed(() => mockDataStore.departments)

const zoneStats = computed(() => {
  const stats = mockDataStore.usageStats.filter(s => s.zone === activeZone.value)
  const totalCallCount = stats.reduce((sum, s) => sum + s.callCount, 0)
  const activeUsers = new Set(stats.map(s => s.username)).size
  const deepUsers = stats.filter(s => s.isDeepUser).length
  const avgCallPerUser = activeUsers > 0 ? Math.round(totalCallCount / activeUsers) : 0
  
  return { totalCallCount, activeUsers, deepUsers, avgCallPerUser }
})

const loadData = () => {}
const resetFilters = () => {
  filters.tool = ''
  filters.department = ''
  filters.dateRange = []
}

const initCharts = () => {
  if (deptChartRef.value) {
    const deptData = mockDataStore.usageStats
      .filter(s => s.zone === activeZone.value)
      .reduce((acc, s) => {
        acc[s.department] = (acc[s.department] || 0) + s.callCount
        return acc
      }, {} as Record<string, number>)
    
    const sortedDept = Object.entries(deptData)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
    
    const chart = echarts.init(deptChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: sortedDept.map(d => d[0]), inverse: true },
      series: [{
        type: 'bar',
        data: sortedDept.map(d => d[1]),
        itemStyle: { color: '#409eff', borderRadius: [0, 4, 4, 0] }
      }]
    })
  }
  
  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: ['04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07'] },
      yAxis: { type: 'value' },
      series: [
        {
          name: '调用量',
          type: 'line',
          data: [1200, 1500, 1800, 2000, 2200, 2500, 2800],
          smooth: true,
          areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
        },
        {
          name: 'DAU',
          type: 'line',
          data: [100, 120, 140, 160, 180, 200, 220],
          smooth: true
        }
      ]
    })
  }
}

watch(activeZone, () => {
  setTimeout(initCharts, 100)
})

onMounted(() => {
  setTimeout(initCharts, 100)
})
</script>

<style scoped>
.usage-page {
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

.zone-card {
  border: none;
  border-radius: 16px;
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

.zone-content {
  padding: 16px 0;
}

.filters {
  margin-bottom: 24px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.stat-row {
  margin: 0 0 24px 0;
}

.stat-item {
  background: #fff;
  padding: 20px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-yellow .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.stat-blue .stat-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
}

.stat-green .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.chart-card {
  background: #fff;
  padding: 20px;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
