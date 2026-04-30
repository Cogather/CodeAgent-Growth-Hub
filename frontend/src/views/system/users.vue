<template>
  <div class="system-page">
    <div class="page-header">
      <div class="page-title">
        <h2>用户与角色</h2>
        <p>管理系统用户与角色权限</p>
      </div>
      <div class="page-action">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" effect="dark">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="editRow(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="dialogVisible" title="用户管理" width="500px" class="form-dialog">
      <el-form :model="form" label-position="top">
        <el-form-item label="工号" required>
          <el-input v-model="form.username" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="部门" required>
          <el-select v-model="form.department" placeholder="请选择" style="width: 100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'
import type { User } from '@/types'

const mockDataStore = useMockDataStore()

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentEditId = ref<number | null>(null)

const form = reactive({
  username: '',
  name: '',
  department: '',
  role: 'user' as 'user' | 'admin'
})

const departments = computed(() => mockDataStore.departments)

const users = ref<User[]>([
  { id: 1, username: 'admin', name: '管理员', department: '研发部', role: 'admin' },
  { id: 2, username: '10001', name: '张三', department: '研发部', role: 'user' },
  { id: 3, username: '10002', name: '李四', department: '测试部', role: 'user' }
])

const showAddDialog = () => {
  isEdit.value = false
  currentEditId.value = null
  Object.keys(form).forEach(key => {
    (form as any)[key] = key === 'role' ? 'user' : ''
  })
  dialogVisible.value = true
}

const editRow = (row: User) => {
  isEdit.value = true
  currentEditId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const deleteRow = async (row: User) => {
  await ElMessageBox.confirm('确定要删除该用户吗?', '提示', { type: 'warning' })
  const idx = users.value.findIndex(u => u.id === row.id)
  if (idx > -1) {
    users.value.splice(idx, 1)
    ElMessage.success('删除成功')
  }
}

const submitForm = () => {
  if (!form.username || !form.name || !form.department) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  if (isEdit.value && currentEditId.value) {
    const idx = users.value.findIndex(u => u.id === currentEditId.value)
    if (idx > -1) {
      users.value[idx] = { ...users.value[idx], ...form }
    }
    ElMessage.success('编辑成功')
  } else {
    users.value.push({
      id: Date.now(),
      ...form
    })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
}
</script>

<style scoped>
.system-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.table-card {
  border: none;
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  --el-table-border-color: #f3f4f6;
  --el-table-header-bg-color: #fafbfc;
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
  color: #374151;
}

:deep(.el-table td.el-table__cell) {
  font-size: 13px;
}

.form-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f3f4f6;
  padding: 16px 20px;
}

.form-dialog :deep(.el-dialog__body) {
  padding: 20px;
}
</style>
