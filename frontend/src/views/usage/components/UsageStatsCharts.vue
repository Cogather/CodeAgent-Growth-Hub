<template>
  <div v-loading="loading || deptLoading" class="stats-body">
    <aside class="dept-panel">
      <div class="panel-title">部门筛选</div>
      <p class="panel-hint">点击部门节点切换统计范围，选中层级下展示下一级子部门对比</p>
      <el-tree
        v-if="deptTree.length"
        ref="treeRef"
        :data="deptTree"
        :props="{ label: 'name', children: 'children' }"
        node-key="dept_code"
        highlight-current
        default-expand-all
        :expand-on-click-node="false"
        @node-click="handleNodeClick"
      />
      <el-empty v-else description="尚未配置组织架构" :image-size="64" />
    </aside>

    <section class="chart-panel">
      <div class="toolbar-row">
        <el-button
          type="primary"
          :loading="exporting"
          :disabled="summary.unused === 0"
          @click="handleExport"
        >
          <el-icon><Download /></el-icon>
          导出未使用人员
        </el-button>
        <span v-if="summary.unused === 0" class="toolbar-hint">当前范围内暂无使用次数为 0 的人员</span>
      </div>

      <div class="summary-row">
        <div class="summary-item">
          <span class="summary-label">统计范围</span>
          <span class="summary-value scope">{{ scopeLabel }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">总人数</span>
          <span class="summary-value">{{ summary.total }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">有使用</span>
          <span class="summary-value used">{{ summary.used }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">未使用</span>
          <span class="summary-value unused">{{ summary.unused }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">使用率</span>
          <span class="summary-value rate">{{ summary.usageRate }}%</span>
        </div>
      </div>

      <div v-if="summary.total === 0" class="empty-chart">
        <el-empty description="当前范围内暂无人员" />
      </div>
      <template v-else>
        <div class="chart-block">
          <h4 class="chart-title">使用情况占比</h4>
          <div ref="pieChartRef" class="chart-container pie" />
        </div>
        <div v-if="childStats.length" class="chart-block">
          <h4 class="chart-title">{{ childLevelLabel }}子部门对比</h4>
          <div ref="barChartRef" class="chart-container bar" />
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ElTree } from 'element-plus'
import { departmentApi } from '@/api/department'
import type { DepartmentNode, UsageStatItem } from '@/types'
import {
  computeChildUsageStats,
  computeUsageSummary,
  filterByDeptPath,
  findDeptNode,
  findDeptPath
} from '@/utils/usageStatsCharts'
import type { ChildDeptStats } from '@/utils/zonePermissionStats'

echarts.use([PieChart, BarChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const USED_COLOR = '#409EFF'
const UNUSED_COLOR = '#C0C4CC'

const props = defineProps<{
  items: UsageStatItem[]
  loading?: boolean
}>()

const emit = defineEmits<{ exportZeroUsage: [deptPath: string[]] }>()

const deptLoading = ref(false)
const exporting = ref(false)
const deptTree = ref<DepartmentNode[]>([])
const selectedDeptCode = ref<string | null>(null)
const treeRef = ref<InstanceType<typeof ElTree>>()
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const pieChart = shallowRef<echarts.ECharts>()
const barChart = shallowRef<echarts.ECharts>()

const selectedPath = computed(() => {
  if (selectedDeptCode.value === null || deptTree.value.length === 0) return [] as string[]
  return findDeptPath(deptTree.value, selectedDeptCode.value) ?? []
})

const scopeLabel = computed(() => {
  if (selectedPath.value.length === 0) return '全部人员'
  return selectedPath.value.join(' / ')
})

const childLevelLabel = computed(() => `${selectedPath.value.length + 1} 级`)

const scopedItems = computed(() => filterByDeptPath(props.items, selectedPath.value))

const summary = computed(() => computeUsageSummary(scopedItems.value))

const selectedNode = computed(() => {
  if (selectedDeptCode.value === null) return null
  return findDeptNode(deptTree.value, selectedDeptCode.value)
})

const childStats = computed<ChildDeptStats[]>(() => {
  const node = selectedNode.value
  if (!node?.children?.length) return []
  return computeChildUsageStats(props.items, selectedPath.value, node.children)
})

const renderPieChart = () => {
  if (!pieChartRef.value) return
  if (!pieChart.value) {
    pieChart.value = echarts.init(pieChartRef.value)
  }
  pieChart.value.setOption(
    {
      color: [USED_COLOR, UNUSED_COLOR],
      tooltip: { trigger: 'item', formatter: '{b}：{c} 人（{d}%）' },
      legend: { bottom: 0, data: ['有使用', '未使用'] },
      series: [
        {
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{c} 人 ({d}%)' },
          data: [
            { name: '有使用', value: summary.value.used },
            { name: '未使用', value: summary.value.unused }
          ]
        }
      ]
    },
    true
  )
}

const renderBarChart = () => {
  if (!barChartRef.value || childStats.value.length === 0) {
    barChart.value?.dispose()
    barChart.value = undefined
    return
  }
  if (!barChart.value) {
    barChart.value = echarts.init(barChartRef.value)
  }
  barChart.value.setOption(
    {
      color: [USED_COLOR, UNUSED_COLOR],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { top: 0, data: ['有使用', '未使用'] },
      grid: { left: 48, right: 24, top: 40, bottom: 32 },
      xAxis: {
        type: 'category',
        data: childStats.value.map((item) => item.name),
        axisLabel: { interval: 0, rotate: childStats.value.length > 5 ? 24 : 0 }
      },
      yAxis: { type: 'value', minInterval: 1, name: '人数' },
      series: [
        {
          name: '有使用',
          type: 'bar',
          stack: 'total',
          data: childStats.value.map((item) => item.withPermission)
        },
        {
          name: '未使用',
          type: 'bar',
          stack: 'total',
          data: childStats.value.map((item) => item.withoutPermission)
        }
      ]
    },
    true
  )
}

const renderCharts = async () => {
  await nextTick()
  if (summary.value.total === 0) {
    pieChart.value?.dispose()
    barChart.value?.dispose()
    pieChart.value = undefined
    barChart.value = undefined
    return
  }
  renderPieChart()
  renderBarChart()
  pieChart.value?.resize()
  barChart.value?.resize()
}

const selectDefaultNode = async () => {
  await nextTick()
  if (deptTree.value.length === 0) {
    selectedDeptCode.value = null
    return
  }
  const rootCode = deptTree.value[0].dept_code
  selectedDeptCode.value = rootCode
  treeRef.value?.setCurrentKey(rootCode)
}

const loadDeptTree = async () => {
  deptLoading.value = true
  try {
    deptTree.value = await departmentApi.getTree()
    await selectDefaultNode()
    await renderCharts()
  } finally {
    deptLoading.value = false
  }
}

const handleNodeClick = (node: DepartmentNode) => {
  selectedDeptCode.value = node.dept_code
}

const handleExport = () => {
  exporting.value = true
  try {
    emit('exportZeroUsage', selectedPath.value)
  } finally {
    exporting.value = false
  }
}

const handleResize = () => {
  pieChart.value?.resize()
  barChart.value?.resize()
}

onMounted(() => {
  loadDeptTree()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart.value?.dispose()
  barChart.value?.dispose()
})

watch([() => props.items, summary, childStats], () => {
  if (!deptLoading.value) {
    renderCharts()
  }
})

defineExpose({ refreshCharts: renderCharts })
</script>

<style scoped>
.stats-body {
  display: flex;
  gap: 20px;
  min-height: 480px;
}

.dept-panel {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid #ebeef5;
  padding-right: 16px;
  max-height: 560px;
  overflow: auto;
}

.panel-title {
  font-weight: 600;
  color: #374151;
  margin: 0 0 4px;
}

.panel-hint {
  font-size: 12px;
  color: #9ca3af;
  margin: 0 0 12px;
  line-height: 1.5;
}

.chart-panel {
  flex: 1;
  min-width: 0;
}

.toolbar-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-hint {
  font-size: 12px;
  color: #9ca3af;
}

.summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: 12px;
  color: #9ca3af;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.summary-value.scope {
  font-size: 14px;
  font-weight: 500;
  max-width: 280px;
  word-break: break-all;
}

.summary-value.used {
  color: #409eff;
}

.summary-value.unused {
  color: #909399;
}

.summary-value.rate {
  color: #67c23a;
}

.chart-block {
  margin-bottom: 20px;
}

.chart-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.chart-container {
  width: 100%;
}

.chart-container.pie {
  height: 280px;
}

.chart-container.bar {
  height: 260px;
}

.empty-chart {
  padding: 48px 0;
}
</style>
