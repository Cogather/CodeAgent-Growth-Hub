<template>
  <div class="users-page">
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <el-button type="primary" :loading="loading" @click="openCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
        <el-button :loading="loading" @click="fetchList">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <p class="toolbar-hint">系统登录账号与业务人员名单独立管理；新建用户会生成临时密码，请私下发给本人</p>
    </el-card>

    <el-card shadow="never" v-loading="loading">
      <el-table :data="items" stripe empty-text="暂无系统用户">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="small" effect="plain">
              {{ row.role === 'admin' ? '管理员' : '只读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small" effect="plain">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="must_change_password" label="须改密" width="100">
          <template #default="{ row }">
            {{ row.must_change_password ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="primary" link size="small" @click="handleResetPassword(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px" destroy-on-close @closed="resetForm">
      <el-form label-width="88px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" :disabled="editingId !== null" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="显示姓名" />
        </el-form-item>
        <el-form-item v-if="editingId === null" label="初始密码">
          <el-input v-model="form.password" type="password" show-password placeholder="留空则自动生成" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="只读" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editingId !== null" label="状态">
          <el-switch v-model="form.isActive" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usersApi } from '@/api/users'
import type { SysUserItem, UserRole } from '@/types'

const loading = ref(false)
const items = ref<SysUserItem[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  username: '',
  name: '',
  password: '',
  role: 'viewer' as UserRole,
  isActive: true
})

const dialogTitle = computed(() => (editingId.value === null ? '新建用户' : '编辑用户'))

const fetchList = async () => {
  loading.value = true
  try {
    const data = await usersApi.list()
    items.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(fetchList)

const resetForm = () => {
  form.username = ''
  form.name = ''
  form.password = ''
  form.role = 'viewer'
  form.isActive = true
  editingId.value = null
}

const openCreate = () => {
  resetForm()
  dialogVisible.value = true
}

const openEdit = (row: SysUserItem) => {
  editingId.value = row.id
  form.username = row.username
  form.name = row.name
  form.role = row.role
  form.isActive = row.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.username.trim() || !form.name.trim()) {
    ElMessage.warning('请填写用户名和姓名')
    return
  }
  try {
    if (editingId.value === null) {
      const result = await usersApi.create({
        username: form.username.trim(),
        name: form.name.trim(),
        role: form.role,
        password: form.password.trim() || undefined
      })
      dialogVisible.value = false
      await fetchList()
      await ElMessageBox.alert(
        `用户已创建。临时密码：${result.temporary_password}\n请私下发给本人，首次登录后须修改密码。`,
        '创建成功',
        { confirmButtonText: '知道了' }
      )
    } else {
      await usersApi.update(editingId.value, {
        name: form.name.trim(),
        role: form.role,
        is_active: form.isActive
      })
      dialogVisible.value = false
      await fetchList()
      ElMessage.success('已更新')
    }
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '操作失败')
  }
}

const handleResetPassword = async (row: SysUserItem) => {
  try {
    await ElMessageBox.confirm(`确定重置「${row.name}」的密码？`, '重置密码', { type: 'warning' })
    const result = await usersApi.resetPassword(row.id)
    await ElMessageBox.alert(
      `新临时密码：${result.temporary_password}\n请私下发给本人，下次登录须修改密码。`,
      '密码已重置',
      { confirmButtonText: '知道了' }
    )
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
</style>
