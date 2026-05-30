<template>
  <div class="zone-perm-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-button v-if="authStore.isAdmin" type="primary" :loading="loading" @click="batchDialogVisible = true">
          <el-icon><Plus /></el-icon>
          批量配置
        </el-button>
        <el-button :loading="loading" @click="fetchList()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="clearFilters">清除筛选</el-button>
        <el-button @click="statsDialogVisible = true">
          <el-icon><PieChart /></el-icon>
          权限统计图
        </el-button>
        <el-input
          v-model="searchText"
          class="search-input"
          clearable
          placeholder="搜索工号或姓名"
          @input="onSearchInput"
          @clear="onSearchInput"
        />
      </div>
      <p class="toolbar-hint">{{ zoneDescription }}</p>
    </el-card>

    <el-card shadow="never" v-loading="loading" class="table-card">
      <div class="table-card-bar">
        <TableRowCount :total="totalAll" :display="total" />
      </div>
      <el-table
        :key="`${zone}-${tableKey}`"
        ref="tableRef"
        :data="items"
        stripe
        empty-text="暂无白名单人员，请批量配置"
        max-height="520"
        @filter-change="onFilterChange"
      >
        <el-table-column prop="emp_no" label="工号" width="120" fixed="left" />
        <el-table-column prop="name" label="姓名" width="100" fixed="left" />
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
          min-width="120"
        >
          <template #default="{ row }">
            {{ row[`dept_l${level}_name` as keyof ZonePermissionItem] || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="模型权限" min-width="220">
          <template #default="{ row }">
            <el-tag v-for="m in row.models" :key="m" size="small" effect="plain" class="model-tag">
              {{ m }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="authStore.isAdmin" label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleRemove(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-bar">
        <el-pagination
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="batchDialogVisible" title="批量配置白名单" width="520px" destroy-on-close @closed="resetBatchForm">
      <el-form label-width="88px">
        <el-form-item label="工号" required>
          <el-input
            v-model="batchForm.empNos"
            type="textarea"
            :rows="3"
            placeholder="逗号分隔，如：10001, 10002, 10003"
          />
        </el-form-item>
        <el-form-item label="模型" required>
          <el-input v-model="batchForm.models" type="textarea" :rows="2" :placeholder="modelHint" />
        </el-form-item>
      </el-form>
      <p class="form-hint">工号必须在「人员名单」中已存在；本批所有工号共用同一组模型权限，已存在则更新</p>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleBatch">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑模型权限" width="440px" destroy-on-close>
      <el-form label-width="88px">
        <el-form-item label="工号">
          <el-input :model-value="editingRow?.emp_no" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input :model-value="editingRow?.name" disabled />
        </el-form-item>
        <el-form-item label="模型" required>
          <el-input v-model="editForm.models" type="textarea" :rows="2" :placeholder="modelHint" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>

    <ZonePermissionStatsDialog
      v-model="statsDialogVisible"
      :zone="zone"
      :permitted-emp-nos="permittedEmpNos"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, type TableInstance } from 'element-plus'
import { PieChart } from '@element-plus/icons-vue'
import TableRowCount from '@/components/TableRowCount.vue'
import { zonePermissionApi } from '@/api/zonePermission'
import { useAuthStore } from '@/stores/auth'
import { DEPT_DISPLAY_LEVELS, ZONE_META, type NetworkZone, type ZonePermissionItem, type ZonePermissionListParams } from '@/types'
import { mergeDeptFiltersFromTable } from '@/utils/serverTableFilters'

type FilterOption = { text: string; value: string }
type ZoneFilters = Pick<
  ZonePermissionListParams,
  'q' | 'dept_l3_name' | 'dept_l4_name' | 'dept_l5_name' | 'dept_l6_name'
>

const authStore = useAuthStore()
const ZonePermissionStatsDialog = defineAsyncComponent(() => import('./ZonePermissionStatsDialog.vue'))

const props = defineProps<{ zone: NetworkZone }>()

const loading = ref(false)
const items = ref<ZonePermissionItem[]>([])
const total = ref(0)
const totalAll = ref(0)
const page = ref(1)
const pageSize = ref(50)
const filters = ref<ZoneFilters>({})
const modelHint = ref('')
const batchDialogVisible = ref(false)
const editDialogVisible = ref(false)
const statsDialogVisible = ref(false)
const editingRow = ref<ZonePermissionItem | null>(null)
const searchText = ref('')
const tableRef = ref<TableInstance>()
const deptFilters = ref<FilterOption[][]>(DEPT_DISPLAY_LEVELS.map(() => []))
const permittedEmpNos = ref<string[]>([])
const tableKey = ref(0)

const batchForm = reactive({ empNos: '', models: '' })
const editForm = reactive({ models: '' })

let searchTimer: number | undefined

const zoneDescription = computed(() => ZONE_META[props.zone].description)

const MODEL_HINTS: Record<NetworkZone, string> = {
  yellow: '如：gpt-4o-mini, claude-3-haiku',
  blue: '如：gpt-4o, claude-3-opus',
  green: '如：gpt-4o, claude-3-5-sonnet'
}

const columnFilteredValue = (level: number) => {
  const key = `dept_l${level}_name` as keyof ZoneFilters
  const value = filters.value[key]
  return value !== undefined ? [value] : undefined
}

const loadDeptFilters = async () => {
  const results = await Promise.all(
    DEPT_DISPLAY_LEVELS.map((level) => zonePermissionApi.distinctValues(props.zone, `dept_l${level}_name`))
  )
  deptFilters.value = results.map((res) =>
    res.values.map((value) => ({ text: value || '（空）', value }))
  )
}

const fetchPermittedEmpNos = async () => {
  try {
    const data = await zonePermissionApi.listEmpNos(props.zone)
    permittedEmpNos.value = data.emp_nos
  } catch {
    permittedEmpNos.value = []
  }
}

const fetchList = async (opts?: { page?: number; resetPage?: boolean }) => {
  if (opts?.resetPage) page.value = 1
  if (opts?.page !== undefined) page.value = opts.page

  loading.value = true
  try {
    const data = await zonePermissionApi.list(props.zone, {
      page: page.value,
      page_size: pageSize.value,
      ...filters.value
    })
    items.value = data.items
    total.value = data.total
    totalAll.value = data.total_all
    page.value = data.page
    pageSize.value = data.page_size
    modelHint.value = MODEL_HINTS[props.zone]
    await fetchPermittedEmpNos()
  } catch (e) {
    items.value = []
    total.value = 0
    ElMessage.error(e instanceof Error ? e.message : '加载白名单失败')
  } finally {
    loading.value = false
  }
}

const onSearchInput = () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    const q = searchText.value.trim()
    filters.value = { ...filters.value, q: q || undefined }
    fetchList({ resetPage: true })
  }, 300)
}

const onFilterChange = (tableFilters: Record<string, string[]>) => {
  const { next, changed } = mergeDeptFiltersFromTable(tableFilters, filters.value)
  if (changed) {
    filters.value = next
    fetchList({ resetPage: true })
  }
}

const clearFilters = async () => {
  searchText.value = ''
  filters.value = {}
  tableKey.value += 1
  await fetchList({ resetPage: true })
}

const handlePageChange = (nextPage: number) => {
  fetchList({ page: nextPage })
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  fetchList({ resetPage: true })
}

watch(
  () => props.zone,
  async () => {
    filters.value = {}
    searchText.value = ''
    page.value = 1
    tableKey.value += 1
    await Promise.all([fetchList(), loadDeptFilters()])
  }
)

onMounted(async () => {
  await Promise.all([fetchList(), loadDeptFilters()])
})

const resetBatchForm = () => {
  batchForm.empNos = ''
  batchForm.models = ''
}

const handleBatch = async () => {
  if (!batchForm.empNos.trim() || !batchForm.models.trim()) {
    ElMessage.warning('请填写工号和模型')
    return
  }
  try {
    const result = await zonePermissionApi.batchUpsert(props.zone, batchForm.empNos, batchForm.models)
    batchDialogVisible.value = false
    await fetchList({ resetPage: true })
    if (result.upserted_count > 0) ElMessage.success(`已配置 ${result.upserted_count} 人`)
    if (result.failures.length > 0) {
      await zonePermissionApi.exportExceptions(props.zone, result.failures)
      ElMessage.warning(`${result.failures.length} 条失败记录已自动导出 Excel`)
    }
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '配置失败')
  }
}

const openEdit = (row: ZonePermissionItem) => {
  editingRow.value = row
  editForm.models = row.models.join(', ')
  editDialogVisible.value = true
}

const handleSaveEdit = async () => {
  if (!editingRow.value || !editForm.models.trim()) {
    ElMessage.warning('请填写模型')
    return
  }
  try {
    await zonePermissionApi.update(props.zone, editingRow.value.emp_no, {
      models_text: editForm.models
    })
    ElMessage.success('已保存')
    editDialogVisible.value = false
    await fetchList()
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '保存失败')
  }
}

const handleRemove = async (row: ZonePermissionItem) => {
  try {
    await ElMessageBox.confirm(`确定将「${row.name}」从${ZONE_META[props.zone].label}白名单移除？`, '确认', {
      type: 'warning'
    })
    await zonePermissionApi.remove(props.zone, row.emp_no)
    ElMessage.success('已移除')
    if (items.value.length === 1 && page.value > 1) {
      await fetchList({ page: page.value - 1 })
    } else {
      await fetchList()
    }
  } catch (e) {
    if (e !== 'cancel' && e instanceof Error) ElMessage.error(e.message)
  }
}
</script>

<style scoped>
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
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

.model-tag {
  margin: 2px 4px 2px 0;
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
