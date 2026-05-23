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
            <el-button @click="clearTableFilters">清除筛选</el-button>
          </div>
          <p class="toolbar-hint">
            展示黄/蓝/绿区白名单并集中的全部有权限人员，使用次数来自 Excel 导入并与名单合并呈现；未导入或导入中无记录的人员显示为 0。数据仅可通过 Excel 导入刷新，不支持在线编辑或删除。
            <span v-if="store.importedAt" class="imported-at">最近导入：{{ store.importedAt }}</span>
          </p>
        </el-card>

        <el-card shadow="never" v-loading="store.loading">
          <el-table
            ref="tableRef"
            :data="store.items"
            stripe
            empty-text="暂无有权限人员，请先在配置中心录入人员并配置网络区域权限"
            max-height="560"
            :default-sort="{ prop: 'usage_count', order: 'descending' }"
          >
            <el-table-column
              prop="display_emp_no"
              label="工号"
              column-key="display_emp_no"
              :filters="displayEmpNoFilters"
              :filter-method="filterByField('display_emp_no')"
              filter-placement="bottom-end"
              min-width="120"
              fixed="left"
            />
            <el-table-column
              prop="name"
              label="姓名"
              column-key="name"
              :filters="nameFilters"
              :filter-method="filterByField('name')"
              filter-placement="bottom-end"
              min-width="110"
              fixed="left"
            />
            <el-table-column
              prop="usage_count"
              label="使用次数"
              sortable
              min-width="120"
              align="right"
            >
              <template #default="{ row }">
                <span :class="{ 'usage-zero': row.usage_count === 0 }">{{ row.usage_count }}</span>
              </template>
            </el-table-column>
            <el-table-column
              v-for="level in DEPT_LEVELS"
              :key="level"
              :prop="`dept_l${level}_name`"
              :label="`${level}级部门`"
              :column-key="`dept_l${level}_name`"
              :filters="deptFilters[level - 1]"
              :filter-method="filterByField(`dept_l${level}_name` as keyof UsageStatItem)"
              filter-placement="bottom-end"
              min-width="130"
            >
              <template #default="{ row }">
                {{ row[`dept_l${level}_name` as keyof UsageStatItem] || '—' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="使用分布" name="charts" lazy>
        <p class="charts-hint">基于「使用数据」中的导入结果统计，切换部门查看有使用与未使用人员分布</p>
        <el-card shadow="never">
          <UsageStatsCharts
            v-if="activeTab === 'charts'"
            ref="chartsRef"
            :items="store.items"
            :loading="store.loading"
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
        Excel 须包含「工号」「使用次数」两列；导入将全量替换已有使用统计数据，不在权限名单中的工号会记入异常并导出
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
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { ElMessage, type TabPaneName, type TableInstance, type UploadFile, type UploadInstance } from 'element-plus'
import { useUsageStatsStore } from '@/stores/usageStats'
import { useAuthStore } from '@/stores/auth'
import { DEPT_LEVELS, type UsageStatItem } from '@/types'

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

const buildFilters = (items: UsageStatItem[], field: keyof UsageStatItem): FilterOption[] => {
  const values = new Set<string>()
  for (const item of items) {
    const raw = item[field]
    values.add(typeof raw === 'string' ? raw : '')
  }
  return Array.from(values)
    .sort((a, b) => a.localeCompare(b, 'zh-CN'))
    .map((v) => ({ text: v || '（空）', value: v }))
}

const displayEmpNoFilters = computed(() => buildFilters(store.items, 'display_emp_no'))
const nameFilters = computed(() => buildFilters(store.items, 'name'))
const deptFilters = computed(() =>
  Array.from({ length: DEPT_LEVELS }, (_, i) => {
    const field = `dept_l${i + 1}_name` as keyof UsageStatItem
    return buildFilters(store.items, field)
  })
)

const filterByField = (field: keyof UsageStatItem) => {
  return (value: string, row: UsageStatItem) => {
    const cell = row[field]
    return (cell ?? '') === value
  }
}

const clearTableFilters = () => {
  tableRef.value?.clearFilter()
}

const handleTabChange = (name: TabPaneName) => {
  if (name === 'charts') {
    chartsRef.value?.refreshCharts()
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

onMounted(() => {
  store.fetchList()
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
</style>
