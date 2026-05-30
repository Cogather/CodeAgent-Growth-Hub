<template>
  <div class="usage-page">
    <el-tabs v-model="activeTab" class="usage-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="使用数据" name="data">
        <el-card shadow="never" class="toolbar-card">
          <div class="toolbar">
            <el-button v-if="authStore.isAdmin" type="primary" :loading="store.loading" @click="importDialogVisible = true">
              <el-icon><Upload /></el-icon>
              导入 Excel
            </el-button>
            <el-button :loading="store.loading" @click="store.downloadTemplate()">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button :loading="store.loading" @click="store.fetchList()">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="clearFilters">清除筛选</el-button>
            <el-input
              v-model="searchText"
              class="search-input"
              clearable
              placeholder="搜索工号或姓名"
              @input="onSearchInput"
              @clear="onSearchInput"
            />
          </div>
          <p class="toolbar-hint">
            展示黄区与绿区白名单并集中的有权限人员（同一工具），使用次数来自 Excel 导入；未导入或无记录显示为 0。蓝区暂不纳入本统计。
            <span v-if="store.importedAt" class="imported-at">最近导入：{{ store.importedAt }}</span>
          </p>
        </el-card>

        <el-card shadow="never" v-loading="store.loading" class="table-card">
          <div class="table-card-bar">
            <TableRowCount :total="store.totalAll" :display="store.total" />
          </div>
          <el-table
            :key="tableKey"
            ref="tableRef"
            :data="store.items"
            stripe
            empty-text="暂无黄/绿区有权限人员，请先在配置中心录入人员并配置黄区或绿区权限"
            max-height="560"
            @filter-change="onFilterChange"
          >
            <el-table-column prop="emp_no" label="工号" min-width="120" fixed="left" />
            <el-table-column prop="name" label="姓名" min-width="110" fixed="left" />
            <el-table-column prop="usage_count" label="使用次数" min-width="100" align="right">
              <template #default="{ row }">
                <span :class="{ 'usage-zero': row.usage_count === 0 }">{{ row.usage_count }}</span>
              </template>
            </el-table-column>
            <el-table-column
              v-for="(level, deptIdx) in DEPT_DISPLAY_LEVELS"
              :key="level"
              :prop="`dept_l${level}_name`"
              :label="`${level}级部门`"
              :column-key="`dept_l${level}_name`"
              :filters="deptFilters[deptIdx]"
              :filtered-value="columnFilteredValue(level)"
              :filter-multiple="false"
              filter-placement="bottom-end"
              min-width="130"
            >
              <template #default="{ row }">
                {{ row[`dept_l${level}_name` as keyof UsageStatItem] || '—' }}
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-bar">
            <el-pagination
              :current-page="store.page"
              :page-size="store.pageSize"
              :total="store.total"
              :page-sizes="[20, 50, 100, 200]"
              layout="total, sizes, prev, pager, next, jumper"
              background
              @current-change="handlePageChange"
              @size-change="handlePageSizeChange"
            />
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="使用分布" name="charts" lazy>
        <p class="charts-hint">基于当前筛选条件下的黄/绿区人员统计有使用与未使用分布（切换至本 Tab 时加载全量筛选结果）</p>
        <el-card shadow="never" v-loading="chartsLoading">
          <UsageStatsCharts
            v-if="activeTab === 'charts'"
            ref="chartsRef"
            :items="chartItems"
            :loading="chartsLoading"
            @export-zero-usage="handleExportZeroUsage"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="importDialogVisible" title="导入使用统计 Excel" width="480px" destroy-on-close @closed="resetImport">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xlsm"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      </el-upload>
      <p class="form-hint">
        Excel 须包含「工号」「使用次数」两列；导入将全量替换已有使用统计数据。仅接受已在黄区或绿区白名单中的工号，其余记入异常并导出
      </p>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="store.loading" :disabled="!selectedFile" @click="handleImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, nextTick, onMounted, ref } from 'vue'
import { ElMessage, type TabPaneName, type TableInstance, type UploadFile, type UploadInstance } from 'element-plus'
import TableRowCount from '@/components/TableRowCount.vue'
import { usageStatsApi } from '@/api/usageStats'
import { useUsageStatsStore, type UsageFilters } from '@/stores/usageStats'
import { useAuthStore } from '@/stores/auth'
import { DEPT_DISPLAY_LEVELS, type UsageStatItem } from '@/types'
import { mergeDeptFiltersFromTable } from '@/utils/serverTableFilters'

const UsageStatsCharts = defineAsyncComponent(() => import('./components/UsageStatsCharts.vue'))

type FilterOption = { text: string; value: string }

const authStore = useAuthStore()
const store = useUsageStatsStore()
const tableRef = ref<TableInstance>()
const chartsRef = ref<{ refreshCharts: () => void }>()
const uploadRef = ref<UploadInstance>()
const importDialogVisible = ref(false)
const selectedFile = ref<File | null>(null)
const activeTab = ref('data')
const searchText = ref('')
const deptFilters = ref<FilterOption[][]>(DEPT_DISPLAY_LEVELS.map(() => []))
const chartItems = ref<UsageStatItem[]>([])
const chartsLoading = ref(false)
const tableKey = ref(0)

let searchTimer: number | undefined

const columnFilteredValue = (level: number) => {
  const key = `dept_l${level}_name` as keyof UsageFilters
  const value = store.filters[key]
  return value !== undefined ? [value] : undefined
}

const loadDeptFilters = async () => {
  const results = await Promise.all(
    DEPT_DISPLAY_LEVELS.map((level) => usageStatsApi.distinctValues(`dept_l${level}_name`))
  )
  deptFilters.value = results.map((res) =>
    res.values.map((value) => ({ text: value || '（空）', value }))
  )
}

const onSearchInput = () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    const q = searchText.value.trim()
    store.setFilters({ ...store.filters, q: q || undefined })
  }, 300)
}

const onFilterChange = (tableFilters: Record<string, string[]>) => {
  const { next, changed } = mergeDeptFiltersFromTable(tableFilters, store.filters)
  if (changed) {
    store.setFilters(next)
  }
}

const clearFilters = async () => {
  searchText.value = ''
  tableKey.value += 1
  await store.setFilters({})
}

const handlePageChange = (page: number) => {
  store.setPage(page)
}

const handlePageSizeChange = (size: number) => {
  store.setPageSize(size)
}

const loadChartItems = async () => {
  chartsLoading.value = true
  try {
    chartItems.value = await store.fetchAllItems({ ...store.filters })
    await nextTick()
    chartsRef.value?.refreshCharts()
  } catch (e) {
    chartItems.value = []
    ElMessage.error(e instanceof Error ? e.message : '加载图表数据失败')
  } finally {
    chartsLoading.value = false
  }
}

const handleTabChange = async (name: TabPaneName) => {
  if (name === 'charts') {
    await nextTick()
    await loadChartItems()
  }
}

const handleExportZeroUsage = async (deptPath: string[]) => {
  try {
    await store.exportZeroUsage(deptPath)
    ElMessage.success('未使用人员已导出')
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '导出失败')
  }
}

const resetImport = () => {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

const handleFileChange = (uploadFile: UploadFile) => {
  selectedFile.value = uploadFile.raw ?? null
}

const handleExceed = () => {
  ElMessage.warning('每次仅支持上传一个文件')
}

const handleImport = async () => {
  if (!selectedFile.value) return

  try {
    const result = await store.importExcel(selectedFile.value)
    importDialogVisible.value = false
    await loadDeptFilters()

    if (result.imported_count > 0) {
      ElMessage.success(`成功导入 ${result.imported_count} 条使用记录`)
    }
    if (result.failures.length > 0) {
      await store.exportExceptions(result.failures)
      ElMessage.warning(`${result.failures.length} 条异常记录已导出 Excel`)
    } else if (result.imported_count === 0) {
      ElMessage.info('没有成功导入的使用记录')
    }
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '导入失败')
  }
}

onMounted(async () => {
  await Promise.all([store.fetchList(), loadDeptFilters()])
})
</script>

<style scoped>
.usage-page {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 220px;
  margin-left: auto;
}

.toolbar-hint {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
  line-height: 1.6;
}

.imported-at {
  margin-left: 12px;
  color: #6b7280;
}

.usage-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.charts-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: #9ca3af;
  line-height: 1.5;
}

.form-hint {
  margin-top: 12px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.5;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 8px;
}

.usage-zero {
  color: #9ca3af;
}

.table-card :deep(.el-card__body) {
  padding-top: 12px;
}

.table-card-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
