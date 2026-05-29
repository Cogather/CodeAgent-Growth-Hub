<template>
  <div class="dept-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            v-if="authStore.isAdmin && !deptStore.rootStatus.has_root"
            type="primary"
            :loading="deptStore.loading"
            @click="openCreate(null)"
          >
            <el-icon><Plus /></el-icon>
            创建根部门
          </el-button>
          <el-button :loading="deptStore.loading" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <span class="toolbar-hint">全局仅一个根节点，其下逐级添加子部门；部门编码为唯一标识</span>
      </div>
    </el-card>

    <el-card shadow="never" v-loading="deptStore.loading">
      <template #header>
        <span class="card-title">部门树</span>
      </template>

      <el-empty v-if="!deptStore.rootStatus.has_root" description="尚未配置根部门">
        <el-button v-if="authStore.isAdmin" type="primary" @click="openCreate(null)">创建根部门</el-button>
      </el-empty>

      <el-tree
        v-else
        :key="treeKey"
        lazy
        :load="loadNode"
        :props="treeProps"
        node-key="dept_code"
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">
              {{ node.label }}
              <el-tag size="small" type="info" effect="plain">{{ data.dept_code }}</el-tag>
              <el-tag v-if="data.parent_dept_code === null" size="small" type="warning" effect="plain">根</el-tag>
            </span>
            <span class="node-actions" @click.stop>
              <el-button type="primary" link size="small" @click="openCreate(data.dept_code)">
                添加子部门
              </el-button>
              <el-button type="primary" link size="small" @click="openEdit(data)">重命名</el-button>
              <el-button
                type="danger"
                link
                size="small"
                :disabled="data.has_children"
                @click="handleDelete(data)"
              >
                删除
              </el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form @submit.prevent="handleSubmit">
        <template v-if="dialogMode === 'create'">
          <el-form-item v-if="!isBatchCreate" label="部门编码" required>
            <el-input
              v-model="formDeptCode"
              placeholder="唯一编码，如 ICT-BG"
              maxlength="64"
              autofocus
            />
          </el-form-item>
          <el-form-item :label="isBatchCreate ? '子部门列表' : '部门名称'" required>
            <el-input
              v-if="!isBatchCreate"
              v-model="formName"
              placeholder="请输入部门名称"
              maxlength="128"
            />
            <el-input
              v-else
              v-model="formName"
              type="textarea"
              :rows="4"
              placeholder="每行一条：部门名称,部门编码&#10;如：研发部,RD01"
              autofocus
            />
          </el-form-item>
          <p v-if="isBatchCreate" class="form-hint">每行格式：名称,编码（支持中英文逗号分隔名称与编码）</p>
        </template>
        <template v-else>
          <el-form-item label="部门编码">
            <el-input :model-value="editingDeptCode ?? ''" disabled />
          </el-form-item>
          <el-form-item label="部门名称" required>
            <el-input v-model="formName" placeholder="请输入部门名称" maxlength="128" autofocus />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="deptStore.loading"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { departmentApi } from '@/api/department'
import { useDepartmentStore } from '@/stores/department'
import { useAuthStore } from '@/stores/auth'
import type { DepartmentLazyNode } from '@/types'

const authStore = useAuthStore()
const deptStore = useDepartmentStore()
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const parentDeptCode = ref<string | null>(null)
const editingDeptCode = ref<string | null>(null)
const formName = ref('')
const formDeptCode = ref('')
const treeKey = ref(0)

const treeProps = {
  label: 'name',
  children: 'children',
  isLeaf: 'isLeaf'
}

const dialogTitle = computed(() => {
  if (dialogMode.value === 'edit') return '重命名部门'
  return parentDeptCode.value === null ? '创建根部门' : '添加子部门'
})

const isBatchCreate = computed(
  () => dialogMode.value === 'create' && parentDeptCode.value !== null
)

const canSubmit = computed(() => {
  if (dialogMode.value === 'edit') return formName.value.trim().length > 0
  if (isBatchCreate.value) return parseBatchItems(formName.value).length > 0
  return formName.value.trim().length > 0 && formDeptCode.value.trim().length > 0
})

/** 批量：每行 名称,编码 */
const parseBatchItems = (input: string): { name: string; dept_code: string }[] => {
  const seen = new Set<string>()
  const result: { name: string; dept_code: string }[] = []
  for (const line of input.split(/\n/)) {
    const trimmed = line.trim()
    if (!trimmed) continue
    const parts = trimmed.split(/[,，]/)
    if (parts.length < 2) continue
    const name = parts[0].trim()
    const dept_code = parts.slice(1).join(',').trim()
    if (!name || !dept_code || seen.has(dept_code)) continue
    seen.add(dept_code)
    result.push({ name, dept_code })
  }
  return result
}

const reloadTree = () => {
  treeKey.value += 1
}

const loadNode = async (node: Node, resolve: (data: DepartmentLazyNode[]) => void) => {
  try {
    const parentCode = node.level === 0 ? null : (node.data.dept_code as string)
    const children = await departmentApi.getChildren(parentCode)
    resolve(
      children.map((item) => ({
        ...item,
        isLeaf: !item.has_children
      }))
    )
  } catch {
    resolve([])
  }
}

const resetForm = () => {
  formName.value = ''
  formDeptCode.value = ''
}

const handleRefresh = async () => {
  await deptStore.refreshStatus()
  reloadTree()
}

onMounted(() => {
  deptStore.fetchRootStatus()
})

const openCreate = (parentCode: string | null) => {
  dialogMode.value = 'create'
  parentDeptCode.value = parentCode
  editingDeptCode.value = null
  resetForm()
  dialogVisible.value = true
}

const openEdit = (node: DepartmentLazyNode) => {
  dialogMode.value = 'edit'
  editingDeptCode.value = node.dept_code
  formName.value = node.name
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (dialogMode.value === 'create') {
      if (parentDeptCode.value === null) {
        const name = formName.value.trim()
        const deptCode = formDeptCode.value.trim()
        if (!name || !deptCode) return
        await deptStore.createDepartment(null, deptCode, name)
        ElMessage.success('添加成功')
      } else {
        const items = parseBatchItems(formName.value)
        if (items.length === 0) return
        await deptStore.createDepartmentsBatch(parentDeptCode.value, items)
        ElMessage.success(`已添加 ${items.length} 个子部门`)
      }
    } else if (editingDeptCode.value !== null) {
      const name = formName.value.trim()
      if (!name) return
      await deptStore.updateDepartment(editingDeptCode.value, name)
      ElMessage.success('已更新')
    }
    dialogVisible.value = false
    reloadTree()
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '操作失败')
  }
}

const handleDelete = async (node: DepartmentLazyNode) => {
  try {
    await ElMessageBox.confirm(`确定删除「${node.name}」？`, '删除确认', { type: 'warning' })
    await deptStore.deleteDepartment(node.dept_code)
    ElMessage.success('已删除')
    reloadTree()
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
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-hint {
  font-size: 13px;
  color: #9ca3af;
}

.card-title {
  font-weight: 600;
  color: #374151;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
}

.node-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

:deep(.el-tree-node__content:hover) .node-actions {
  opacity: 1;
}

.form-hint {
  margin: -8px 0 0;
  font-size: 12px;
  color: #9ca3af;
}
</style>
