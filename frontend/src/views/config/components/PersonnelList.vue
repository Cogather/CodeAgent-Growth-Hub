<template>
  <div class="personnel-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-button type="primary" :loading="personnelStore.loading" @click="importDialogVisible = true">
          <el-icon><Plus /></el-icon>
          批量导入工号
        </el-button>
        <el-button :loading="personnelStore.loading" @click="personnelStore.fetchList()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="clearTableFilters">清除筛选</el-button>
      </div>
      <p class="toolbar-hint">
        填写工号后从 HR 系统查询姓名与七级部门信息并入库；一级部门须与组织架构根节点一致，异常记录自动导出 Excel
      </p>
    </el-card>

    <el-card shadow="never" v-loading="personnelStore.loading">
      <el-table
        ref="tableRef"
        :data="personnelStore.items"
        stripe
        empty-text="暂无人员，请批量导入工号"
        max-height="560"
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
          v-for="level in DEPT_LEVELS"
          :key="level"
          :prop="`dept_l${level}_name`"
          :label="`${level}级部门`"
          :column-key="`dept_l${level}_name`"
          :filters="deptFilters[level - 1]"
          :filter-method="filterByField(`dept_l${level}_name` as keyof PersonnelItem)"
          filter-placement="bottom-end"
          min-width="130"
        >
          <template #default="{ row }">
            {{ row[`dept_l${level}_name` as keyof PersonnelItem] || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="importDialogVisible" title="批量导入工号" width="480px" destroy-on-close @closed="importText = ''">
      <el-input
        v-model="importText"
        type="textarea"
        :rows="4"
        placeholder="多个工号用逗号分隔，如：10001, 10002, 10003"
        autofocus
      />
      <p class="form-hint">部门名称与编码由 HR 系统返回，直接写入人员表，不关联部门树</p>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="personnelStore.loading" :disabled="!importText.trim()" @click="handleImport">
          导入
        </el-button>
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
        <template v-for="level in DEPT_LEVELS" :key="level">
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
import { usePersonnelStore } from '@/stores/personnel'
import { DEPT_LEVELS, type PersonnelItem, type PersonnelUpdatePayload } from '@/types'

type FilterOption = { text: string; value: string }

const personnelStore = usePersonnelStore()
const tableRef = ref<TableInstance>()
const importDialogVisible = ref(false)
const editDialogVisible = ref(false)
const importText = ref('')
const editingEmpNo = ref('')

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

const buildFilters = (items: PersonnelItem[], field: keyof PersonnelItem): FilterOption[] => {
  const values = new Set<string>()
  for (const item of items) {
    const raw = item[field]
    values.add(typeof raw === 'string' ? raw : '')
  }
  return Array.from(values)
    .sort((a, b) => a.localeCompare(b, 'zh-CN'))
    .map((v) => ({ text: v || '（空）', value: v }))
}

const displayEmpNoFilters = computed(() => buildFilters(personnelStore.items, 'display_emp_no'))
const nameFilters = computed(() => buildFilters(personnelStore.items, 'name'))

const deptFilters = computed(() =>
  Array.from({ length: DEPT_LEVELS }, (_, i) => {
    const field = `dept_l${i + 1}_name` as keyof PersonnelItem
    return buildFilters(personnelStore.items, field)
  })
)

const filterByField = (field: keyof PersonnelItem) => {
  return (value: string, row: PersonnelItem) => {
    const cell = row[field]
    return (cell ?? '') === value
  }
}

const clearTableFilters = () => {
  tableRef.value?.clearFilter()
}

onMounted(() => {
  personnelStore.fetchList()
})

const handleImport = async () => {
  const text = importText.value.trim()
  if (!text) return

  try {
    const result = await personnelStore.batchImport(text)
    importDialogVisible.value = false

    if (result.imported_count > 0) {
      ElMessage.success(`成功导入 ${result.imported_count} 人`)
    }
    if (result.failures.length > 0) {
      await personnelStore.exportExceptions(result.failures)
      ElMessage.warning(`${result.failures.length} 条异常记录已导出 Excel`)
    } else if (result.imported_count === 0) {
      ElMessage.info('没有成功导入的人员')
    }
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '导入失败')
  }
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
    await ElMessageBox.confirm(`确定移除「${row.name}」（${row.display_emp_no}）？`, '移除确认', {
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

.edit-form {
  max-height: 420px;
  overflow-y: auto;
  padding-right: 8px;
}
</style>
