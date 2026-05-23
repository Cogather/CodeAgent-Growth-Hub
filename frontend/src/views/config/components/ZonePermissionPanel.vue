<template>
  <div class="zone-perm-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-button type="primary" :loading="loading" @click="batchDialogVisible = true">
          <el-icon><Plus /></el-icon>
          批量配置
        </el-button>
        <el-button :loading="loading" @click="fetchList">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="statsDialogVisible = true">
          <el-icon><PieChart /></el-icon>
          权限统计图
        </el-button>
      </div>
      <p class="toolbar-hint">{{ zoneDescription }}</p>
    </el-card>

    <el-card shadow="never" v-loading="loading">
      <el-table :data="items" stripe empty-text="暂无白名单人员，请批量配置" max-height="520">
        <el-table-column prop="display_emp_no" label="工号" width="120" fixed="left" />
        <el-table-column prop="name" label="姓名" width="100" fixed="left" />
        <el-table-column label="模型权限" min-width="280">
          <template #default="{ row }">
            <el-tag v-for="m in row.models" :key="m" size="small" effect="plain" class="model-tag">
              {{ m }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleRemove(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
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
          <el-input :model-value="editingRow?.display_emp_no" disabled />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { PieChart } from '@element-plus/icons-vue'
import { zonePermissionApi } from '@/api/zonePermission'
import { ZONE_META, type NetworkZone, type ZonePermissionItem } from '@/types'

const ZonePermissionStatsDialog = defineAsyncComponent(() => import('./ZonePermissionStatsDialog.vue'))

const props = defineProps<{ zone: NetworkZone }>()

const loading = ref(false)
const items = ref<ZonePermissionItem[]>([])
const modelHint = ref('')
const batchDialogVisible = ref(false)
const editDialogVisible = ref(false)
const statsDialogVisible = ref(false)
const editingRow = ref<ZonePermissionItem | null>(null)

const batchForm = reactive({ empNos: '', models: '' })
const editForm = reactive({ models: '' })

const zoneDescription = computed(() => ZONE_META[props.zone].description)
const permittedEmpNos = computed(() => items.value.map((item) => item.emp_no))

const MODEL_HINTS: Record<NetworkZone, string> = {
  yellow: '如：gpt-4o-mini, claude-3-haiku',
  blue: '如：gpt-4o, claude-3-opus',
  green: '如：gpt-4o, claude-3-5-sonnet'
}

const fetchList = async () => {
  loading.value = true
  try {
    const data = await zonePermissionApi.list(props.zone)
    items.value = data.items
    modelHint.value = MODEL_HINTS[props.zone]
  } finally {
    loading.value = false
  }
}

watch(() => props.zone, fetchList)
onMounted(fetchList)

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
    await fetchList()
    if (result.upserted_count > 0) ElMessage.success(`已配置 ${result.upserted_count} 人`)
    if (result.failures.length > 0) {
      const detail = result.failures.map((f) => `${f.emp_no}：${f.reason}`).join('；')
      ElMessage.warning({ message: `${result.failures.length} 条失败：${detail}`, duration: 6000 })
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
    await fetchList()
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
</style>
