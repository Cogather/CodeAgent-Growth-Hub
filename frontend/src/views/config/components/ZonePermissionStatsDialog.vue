<template>
  <el-dialog
    v-model="visible"
    :title="`${zoneLabel}权限覆盖统计`"
    width="920px"
    destroy-on-close
    class="stats-dialog"
    @opened="handleOpened"
    @closed="handleClosed"
  >
    <div v-loading="loading" class="stats-body">
      <aside class="dept-panel">
        <div class="panel-title">部门筛选</div>
        <p class="panel-hint">点击部门节点切换统计范围，选中层级下展示下一级子部门对比</p>
        <el-tree
          v-if="deptTree.length"
          ref="treeRef"
          :data="deptTree"
          :props="{ label: 'name', children: 'children' }"
          node-key="id"
          highlight-current
          default-expand-all
          :expand-on-click-node="false"
          @node-click="handleNodeClick"
        />
        <el-empty v-else description="尚未配置组织架构" :image-size="64" />
      </aside>

      <section class="chart-panel">
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
            <span class="summary-label">有权限</span>
            <span class="summary-value with">{{ summary.withPermission }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">无权限</span>
            <span class="summary-value without">{{ summary.withoutPermission }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">覆盖率</span>
            <span class="summary-value rate">{{ summary.coverageRate }}%</span>
          </div>
        </div>

        <div v-if="summary.total === 0" class="empty-chart">
          <el-empty description="当前范围内暂无人员" />
        </div>
        <template v-else>
          <div class="chart-block">
            <h4 class="chart-title">权限覆盖占比</h4>
            <div ref="pieChartRef" class="chart-container pie" />
          </div>
          <div v-if="childStats.length" class="chart-block">
            <h4 class="chart-title">{{ childLevelLabel }}子部门对比</h4>
            <div ref="barChartRef" class="chart-container bar" />
          </div>
        </template>
      </section>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, shallowRef, watch } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ElTree } from 'element-plus'
import { personnelApi } from '@/api/personnel'
import { departmentApi } from '@/api/department'
import type { DepartmentNode, NetworkZone, PersonnelItem } from '@/types'
import { ZONE_META } from '@/types'
import {
  computeChildDeptStats,
  computePermissionSummary,
  filterPersonnelByDeptPath,
  findDeptNode,
  findDeptPath,
  type ChildDeptStats,
  type PermissionSummary
} from '@/utils/zonePermissionStats'

echarts.use([PieChart, BarChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const ZONE_COLORS: Record<NetworkZone, string> = {
  yellow: '#E6A23C',
  blue: '#409EFF',
  green: '#67C23A'
}

const props = defineProps<{
  modelValue: boolean
  zone: NetworkZone
  permittedEmpNos: string[]
}>()

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const personnel = ref<PersonnelItem[]>([])
const deptTree = ref<DepartmentNode[]>([])
const selectedDeptId = ref<number | null>(null)
const treeRef = ref<InstanceType<typeof ElTree>>()
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const pieChart = shallowRef<echarts.ECharts>()
const barChart = shallowRef<echarts.ECharts>()

const zoneLabel = computed(() => ZONE_META[props.zone].label)
const permittedSet = computed(() => new Set(props.permittedEmpNos))

const selectedPath = computed(() => {
  if (selectedDeptId.value === null || deptTree.value.length === 0) return [] as string[]
  return findDeptPath(deptTree.value, selectedDeptId.value) ?? []
})

const scopeLabel = computed(() => {
  if (selectedPath.value.length === 0) return '全部人员'
  return selectedPath.value.join(' / ')
})

const childLevelLabel = computed(() => {
  const level = selectedPath.value.length + 1
  return `${level} 级`
})

const scopedPersonnel = computed(() => filterPersonnelByDeptPath(personnel.value, selectedPath.value))

const summary = computed<PermissionSummary>(() =>
  computePermissionSummary(scopedPersonnel.value, permittedSet.value)
)

const selectedNode = computed(() => {
  if (selectedDeptId.value === null) return null
  return findDeptNode(deptTree.value, selectedDeptId.value)
})

const childStats = computed<ChildDeptStats[]>(() => {
  const node = selectedNode.value
  if (!node?.children?.length) return []
  return computeChildDeptStats(personnel.value, selectedPath.value, node.children, permittedSet.value)
})

const renderPieChart = () => {
  if (!pieChartRef.value) return
  if (!pieChart.value) {
    pieChart.value = echarts.init(pieChartRef.value)
  }
  const zoneColor = ZONE_COLORS[props.zone]
  pieChart.value.setOption(
    {
      color: [zoneColor, '#C0C4CC'],
      tooltip: {
        trigger: 'item',
        formatter: '{b}：{c} 人（{d}%）'
      },
      legend: {
        bottom: 0,
        data: ['有权限', '无权限']
      },
      series: [
        {
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: {
            formatter: '{b}\n{c} 人 ({d}%)'
          },
          data: [
            { name: '有权限', value: summary.value.withPermission },
            { name: '无权限', value: summary.value.withoutPermission }
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
  const zoneColor = ZONE_COLORS[props.zone]
  barChart.value.setOption(
    {
      color: [zoneColor, '#C0C4CC'],
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        top: 0,
        data: ['有权限', '无权限']
      },
      grid: { left: 48, right: 24, top: 40, bottom: 32 },
      xAxis: {
        type: 'category',
        data: childStats.value.map((item) => item.name),
        axisLabel: { interval: 0, rotate: childStats.value.length > 5 ? 24 : 0 }
      },
      yAxis: { type: 'value', minInterval: 1, name: '人数' },
      series: [
        {
          name: '有权限',
          type: 'bar',
          stack: 'total',
          data: childStats.value.map((item) => item.withPermission)
        },
        {
          name: '无权限',
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
    selectedDeptId.value = null
    return
  }
  const rootId = deptTree.value[0].id
  selectedDeptId.value = rootId
  treeRef.value?.setCurrentKey(rootId)
}

const loadData = async () => {
  loading.value = true
  try {
    const [personnelRes, tree] = await Promise.all([personnelApi.list(), departmentApi.getTree()])
    personnel.value = personnelRes.items
    deptTree.value = tree
    await selectDefaultNode()
    await renderCharts()
  } finally {
    loading.value = false
  }
}

const handleNodeClick = (node: DepartmentNode) => {
  selectedDeptId.value = node.id
}

const handleOpened = () => {
  loadData()
}

const handleClosed = () => {
  pieChart.value?.dispose()
  barChart.value?.dispose()
  pieChart.value = undefined
  barChart.value = undefined
  personnel.value = []
  deptTree.value = []
  selectedDeptId.value = null
}

const handleResize = () => {
  pieChart.value?.resize()
  barChart.value?.resize()
}

watch([summary, childStats], () => {
  if (visible.value && !loading.value) {
    renderCharts()
  }
})

watch(visible, (open) => {
  if (open) {
    window.addEventListener('resize', handleResize)
  } else {
    window.removeEventListener('resize', handleResize)
  }
})
</script>

<style scoped>
.stats-body {
  display: flex;
  gap: 20px;
  min-height: 420px;
}

.dept-panel {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid #ebeef5;
  padding-right: 16px;
  max-height: 520px;
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

.summary-value.with {
  color: #67c23a;
}

.summary-value.without {
  color: #909399;
}

.summary-value.rate {
  color: #409eff;
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

.stats-dialog :deep(.el-dialog__body) {
  padding-top: 12px;
}
</style>
