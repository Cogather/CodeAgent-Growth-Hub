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
          <el-button :loading="deptStore.loading" @click="deptStore.fetchTree()">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <span class="toolbar-hint">全局仅一个根节点，其下逐级添加子部门</span>
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
        :data="deptStore.tree"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">
              {{ node.label }}
              <el-tag v-if="data.parent_id === null" size="small" type="warning" effect="plain">根</el-tag>
            </span>
            <span class="node-actions" @click.stop>
              <el-button type="primary" link size="small" @click="openCreate(data.id)">添加子部门</el-button>
              <el-button type="primary" link size="small" @click="openEdit(data)">重命名</el-button>
              <el-button
                type="danger"
                link
                size="small"
                :disabled="data.children?.length > 0"
                @click="handleDelete(data)"
              >
                删除
              </el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="440px" destroy-on-close @closed="formName = ''">
      <el-form @submit.prevent="handleSubmit">
        <el-form-item label="部门名称" required>
          <el-input
            v-if="!isBatchCreate"
            v-model="formName"
            placeholder="请输入部门名称"
            maxlength="128"
            autofocus
          />
          <el-input
            v-else
            v-model="formName"
            type="textarea"
            :rows="3"
            placeholder="多个部门用逗号分隔，如：研发部, 产品部, 测试部"
            autofocus
          />
        </el-form-item>
        <p v-if="isBatchCreate" class="form-hint">支持中英文逗号分隔，将一次性创建多个同级子部门</p>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="deptStore.loading" :disabled="!formName.trim()" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useDepartmentStore } from '@/stores/department'
import { useAuthStore } from '@/stores/auth'
import type { DepartmentNode } from '@/types'

const authStore = useAuthStore()
const deptStore = useDepartmentStore()
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const parentId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const formName = ref('')

const dialogTitle = computed(() => {
  if (dialogMode.value === 'edit') return '重命名部门'
  return parentId.value === null ? '创建根部门' : '添加子部门'
})

const isBatchCreate = computed(
  () => dialogMode.value === 'create' && parentId.value !== null
)

/** 按逗号切割，去空白、去重 */
const parseNames = (input: string): string[] => {
  const seen = new Set<string>()
  const result: string[] = []
  for (const part of input.split(/[,，]/)) {
    const name = part.trim()
    if (name && !seen.has(name)) {
      seen.add(name)
      result.push(name)
    }
  }
  return result
}

onMounted(() => {
  deptStore.fetchTree()
})

const openCreate = (pid: number | null) => {
  dialogMode.value = 'create'
  parentId.value = pid
  editingId.value = null
  formName.value = ''
  dialogVisible.value = true
}

const openEdit = (node: DepartmentNode) => {
  dialogMode.value = 'edit'
  editingId.value = node.id
  formName.value = node.name
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const raw = formName.value.trim()
  if (!raw) return

  try {
    if (dialogMode.value === 'create') {
      if (parentId.value === null) {
        await deptStore.createDepartment(null, raw)
        ElMessage.success('添加成功')
      } else {
        const names = parseNames(raw)
        if (names.length === 0) return
        await deptStore.createDepartmentsBatch(parentId.value, names)
        ElMessage.success(`已添加 ${names.length} 个子部门`)
      }
    } else if (editingId.value !== null) {
      await deptStore.updateDepartment(editingId.value, raw)
      ElMessage.success('已更新')
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '操作失败')
  }
}

const handleDelete = async (node: DepartmentNode) => {
  try {
    await ElMessageBox.confirm(`确定删除「${node.name}」？`, '删除确认', { type: 'warning' })
    await deptStore.deleteDepartment(node.id)
    ElMessage.success('已删除')
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
