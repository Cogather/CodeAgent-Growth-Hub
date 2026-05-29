<template>
  <div class="personnel-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-button v-if="authStore.isAdmin" type="primary" :loading="personnelStore.importing" @click="importDialogVisible = true">
          <el-icon><Plus /></el-icon>
          批量导入工号
        </el-button>
        <el-button :loading="personnelStore.loading" @click="personnelStore.fetchList()">
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
        填写工号后从 HR 系统查询姓名与七级部门信息并入库；一级部门须与组织架构根节点一致，异常记录自动导出 Excel
      </p>
    </el-card>

    <el-card shadow="never" v-loading="personnelStore.loading" class="table-card">
      <div class="table-card-bar">
        <TableRowCount :total="personnelStore.total" :display="personnelStore.total" />
      </div>
      <el-table
        ref="tableRef"
        :data="personnelStore.items"
        stripe
        empty-text="暂无人员，请批量导入工号"
        max-height="560"
        @filter-change="onFilterChange"
      >
        <el-table-column prop="emp_no" label="工号" min-width="120" fixed="left" />
        <el-table-column prop="name" label="姓名" min-width="110" fixed="left" />
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
            {{ row[`dept_l${level}_name` as keyof PersonnelItem] || '—' }}
          </template>
        </el-table-column>
        <el-table-column v-if="authStore.isAdmin" label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-bar">
        <el-pagination
          :current-page="personnelStore.page"
          :page-size="personnelStore.pageSize"
          :total="personnelStore.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="importDialogVisible"
      title="批量导入工号"
      width="480px"
      destroy-on-close
      :close-on-click-modal="!personnelStore.importing"
      :show-close="!personnelStore.importing"
      @closed="resetImportDialog"
    >
      <div v-if="personnelStore.importing" class="import-progress">
        <p class="import-progress-title">正在从 HR 查询并写入，已完成的批次会自动保存</p>
        <el-progress :percentage="importPercent" :stroke-width="16" />
        <p class="import-progress-stats">
          已处理 {{ importProgress.processed }} / {{ importProgress.total }} 个工号
          <span v-if="importProgress.importedCount > 0">，成功 {{ importProgress.importedCount }}</span>
          <span v-if="importProgress.failureCount > 0">，异常 {{ importProgress.failureCount }}</span>
        </p>
      </div>
      <template v-else>
        <el-input
          v-model="importText"
          type="textarea"
          :rows="4"
          placeholder="多个工号用逗号分隔，如：10001, 10002, 10003"
          autofocus
        />
        <p class="form-hint">部门名称与编码由 HR 系统返回，直接写入人员表，不关联部门树</p>
        <p class="form-hint">大批量工号将自动分批导入，可随时取消；已导入的批次不会回滚</p>
      </template>
      <template #footer>
        <el-button v-if="personnelStore.importing" @click="handleCancelImport">取消导入</el-button>
        <template v-else>
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" :disabled="!importText.trim()" @click="handleImport">导入</el-button>
        </template>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑人员" width="560px" destroy-on-close>
      <el-form label-width="88px" class="edit-form">
        <el-form-item label="工号">
          <el-input :model-value="editingEmpNo" disabled />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="editForm.name" maxlength="128" />
        </el-form-item>
        <template v-for="level in DEPT_DISPLAY_LEVELS" :key="level">
          <el-form-item :label="`${level}级部门`">
            <el-input v-model="editForm[`dept_l${level}_name`]" maxlength="128" />
          </el-form-item>
          <el-form-item :label="`${level}级编码`">
            <el-input v-model="editForm[`dept_l${level}_code`]" maxlength="64" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="personnelStore.loading" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type TableInstance } from 'element-plus'
import TableRowCount from '@/components/TableRowCount.vue'
import { personnelApi } from '@/api/personnel'
import { usePersonnelStore, type PersonnelFilters } from '@/stores/personnel'
import { useAuthStore } from '@/stores/auth'
import { DEPT_DISPLAY_LEVELS, DEPT_LEVELS, type PersonnelItem, type PersonnelUpdatePayload } from '@/types'
import type { PersonnelImportProgress } from '@/utils/personnelImport'

type FilterOption = { text: string; value: string }

const authStore = useAuthStore()
const personnelStore = usePersonnelStore()
const tableRef = ref<TableInstance>()
const importDialogVisible = ref(false)
const editDialogVisible = ref(false)
const importText = ref('')
const searchText = ref('')
const importAbortController = ref<AbortController | null>(null)
const importProgress = reactive<PersonnelImportProgress>({
  processed: 0,
  total: 0,
  importedCount: 0,
  failureCount: 0,
  cancelled: false
})
const editingEmpNo = ref('')
const deptFilters = ref<FilterOption[][]>(DEPT_DISPLAY_LEVELS.map(() => []))

let searchTimer: number | undefined

const importPercent = computed(() => {
  if (importProgress.total === 0) return 0
  return Math.round((importProgress.processed / importProgress.total) * 100)
})

const emptyDeptFields = (): Record<string, string> => {
  const fields: Record<string, string> = {}
  for (let i = 1; i <= DEPT_LEVELS; i++) {
    fields[`dept_l${i}_name`] = ''
    fields[`dept_l${i}_code`] = ''
  }
  return fields
}

type EditForm = { name: string } & Record<string, string>

const editForm = reactive<EditForm>({
  name: '',
  ...emptyDeptFields()
})

const columnFilteredValue = (level: number) => {
  const key = `dept_l${level}_name` as keyof PersonnelFilters
  const value = personnelStore.filters[key]
  return value !== undefined ? [value] : undefined
}

const loadDeptFilters = async () => {
  const results = await Promise.all(
    DEPT_DISPLAY_LEVELS.map((level) => personnelApi.distinctValues(`dept_l${level}_name`))
  )
  deptFilters.value = results.map((res) =>
    res.values.map((value) => ({ text: value || '（空）', value }))
  )
}

const onSearchInput = () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    const q = searchText.value.trim()
    personnelStore.setFilters({
      ...personnelStore.filters,
      q: q || undefined
    })
  }, 300)
}

const onFilterChange = (filters: Record<string, string[]>) => {
  const next: PersonnelFilters = { ...personnelStore.filters }
  for (const level of DEPT_DISPLAY_LEVELS) {
    const key = `dept_l${level}_name` as keyof PersonnelFilters
    const values = filters[key]
    if (!values || values.length === 0) {
      delete next[key]
    } else {
      next[key] = values[0]
    }
  }
  personnelStore.setFilters(next)
}

const clearFilters = async () => {
  searchText.value = ''
  tableRef.value?.clearFilter()
  await personnelStore.setFilters({})
}

const handlePageChange = (page: number) => {
  personnelStore.setPage(page)
}

const handlePageSizeChange = (size: number) => {
  personnelStore.setPageSize(size)
}

onMounted(async () => {
  await Promise.all([personnelStore.fetchList(), loadDeptFilters()])
})

const resetImportDialog = () => {
  importText.value = ''
  importAbortController.value = null
  importProgress.processed = 0
  importProgress.total = 0
  importProgress.importedCount = 0
  importProgress.failureCount = 0
  importProgress.cancelled = false
}

const handleImport = async () => {
  const text = importText.value.trim()
  if (!text) return

  importAbortController.value = new AbortController()

  try {
    const result = await personnelStore.batchImport(text, {
      signal: importAbortController.value.signal,
      onProgress: (progress) => {
        importProgress.processed = progress.processed
        importProgress.total = progress.total
        importProgress.importedCount = progress.importedCount
        importProgress.failureCount = progress.failureCount
        importProgress.cancelled = progress.cancelled
      }
    })
    importDialogVisible.value = false
    await loadDeptFilters()

    if (result.cancelled) {
      const parts: string[] = [`已取消导入（已完成 ${result.imported_count} 人`]
      if (result.failures.length > 0) {
        parts.push(`，${result.failures.length} 条异常已导出`)
      }
      parts.push('）')
      ElMessage.warning(parts.join(''))
      return
    }

    if (result.imported_count > 0) {
      ElMessage.success(`成功导入 ${result.imported_count} 人`)
    }
    if (result.failures.length > 0) {
      ElMessage.warning(`${result.failures.length} 条异常记录已自动导出 Excel`)
    } else if (result.imported_count === 0) {
      ElMessage.info('没有成功导入的人员')
    }
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '导入失败')
  }
}

const handleCancelImport = () => {
  importAbortController.value?.abort()
}

const openEdit = (row: PersonnelItem) => {
  editingEmpNo.value = row.emp_no
  editForm.name = row.name
  for (let i = 1; i <= DEPT_LEVELS; i++) {
    editForm[`dept_l${i}_name`] = (row[`dept_l${i}_name` as keyof PersonnelItem] as string) || ''
    editForm[`dept_l${i}_code`] = (row[`dept_l${i}_code` as keyof PersonnelItem] as string) || ''
  }
  editDialogVisible.value = true
}

const buildUpdatePayload = (): PersonnelUpdatePayload => {
  const payload = { name: editForm.name.trim() } as PersonnelUpdatePayload
  for (let i = 1; i <= DEPT_LEVELS; i++) {
    const nameKey = `dept_l${i}_name` as keyof PersonnelUpdatePayload
    const codeKey = `dept_l${i}_code` as keyof PersonnelUpdatePayload
    ;(payload as Record<string, string | null>)[nameKey] = editForm[`dept_l${i}_name`].trim() || null
    ;(payload as Record<string, string | null>)[codeKey] = editForm[`dept_l${i}_code`].trim() || null
  }
  return payload
}

const handleSaveEdit = async () => {
  if (!editForm.name.trim()) {
    ElMessage.warning('请填写姓名')
    return
  }

  try {
    await personnelStore.updatePersonnel(editingEmpNo.value, buildUpdatePayload())
    ElMessage.success('已保存')
    editDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '保存失败')
  }
}

const handleDelete = async (row: PersonnelItem) => {
  try {
    await ElMessageBox.confirm(`确定移除「${row.name}」（${row.emp_no}）？`, '移除确认', {
      type: 'warning'
    })
    await personnelStore.deletePersonnel(row.emp_no)
    ElMessage.success('已移除')
  } catch (e) {
    if (e !== 'cancel' && e instanceof Error) {
      ElMessage.error(e.message)
    }
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
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.import-progress {
  padding: 8px 0 4px;
}

.import-progress-title {
  margin: 0 0 16px;
  font-size: 14px;
  color: #4b5563;
}

.import-progress-stats {
  margin: 12px 0 0;
  font-size: 13px;
  color: #6b7280;
}

.edit-form {
  max-height: 420px;
  overflow-y: auto;
  padding-right: 8px;
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
