<template>
  <el-dialog v-model="visible" title="管理重点关注 PDU" width="640px" destroy-on-close @open="handleOpen">
    <p class="hint">
      仅可添加组织树第 {{ targetDepth }} 层节点（四级 PDU）。开启顶栏「PDU 视角」后，各列表仅显示这些部门范围内的人员。
    </p>

    <div class="add-row">
      <el-select
        v-model="selectedCandidate"
        filterable
        clearable
        placeholder="选择四级 PDU 添加"
        class="candidate-select"
        :loading="loadingCandidates"
      >
        <el-option
          v-for="item in candidates"
          :key="item.dept_code"
          :label="formatOption(item)"
          :value="item.dept_code"
        />
      </el-select>
      <el-button type="primary" :disabled="!selectedCandidate" :loading="saving" @click="handleAdd">
        添加
      </el-button>
    </div>

    <el-table v-loading="loading" :data="items" empty-text="暂无关注 PDU" stripe max-height="320">
      <el-table-column label="PDU" min-width="200">
        <template #default="{ row }">
          <div class="name-cell">{{ row.alias || row.name }}</div>
          <div class="path-cell">{{ row.path.join(' / ') }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="dept_code" label="编码" width="140" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="{ row }">
          <el-button type="danger" link size="small" @click="handleRemove(row.dept_code)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { focusPduApi } from '@/api/focusPdu'
import { useFocusPduStore } from '@/stores/focusPdu'
import type { FocusPduItem } from '@/types'

const visible = defineModel<boolean>({ required: true })

const focusPdu = useFocusPduStore()
const items = ref<FocusPduItem[]>([])
const candidates = ref<FocusPduItem[]>([])
const targetDepth = ref(4)
const selectedCandidate = ref('')
const loading = ref(false)
const loadingCandidates = ref(false)
const saving = ref(false)

const formatOption = (item: FocusPduItem) => `${item.name}（${item.path.join(' / ')}）`

const handleOpen = async () => {
  loading.value = true
  loadingCandidates.value = true
  try {
    const [listRes, candRes] = await Promise.all([focusPduApi.list(), focusPduApi.listCandidates()])
    items.value = listRes.items
    targetDepth.value = listRes.target_depth
    candidates.value = candRes.items
    selectedCandidate.value = ''
    await focusPdu.fetchList()
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '加载失败')
  } finally {
    loading.value = false
    loadingCandidates.value = false
  }
}

const handleAdd = async () => {
  if (!selectedCandidate.value) return
  saving.value = true
  try {
    await focusPduApi.add({ dept_code: selectedCandidate.value })
    ElMessage.success('已添加')
    selectedCandidate.value = ''
    await handleOpen()
    window.dispatchEvent(new CustomEvent('focus-pdu-changed'))
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '添加失败')
  } finally {
    saving.value = false
  }
}

const handleRemove = async (deptCode: string) => {
  try {
    await ElMessageBox.confirm('确定移出重点关注列表？', '确认', { type: 'warning' })
    await focusPduApi.remove(deptCode)
    ElMessage.success('已移除')
    await handleOpen()
    window.dispatchEvent(new CustomEvent('focus-pdu-changed'))
  } catch (e) {
    if (e === 'cancel' || e === 'close') return
    ElMessage.error(e instanceof Error ? e.message : '移除失败')
  }
}
</script>

<style scoped>
.hint {
  margin: 0 0 16px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.add-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.candidate-select {
  flex: 1;
}

.name-cell {
  font-weight: 500;
  color: #1f2937;
}

.path-cell {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}
</style>
