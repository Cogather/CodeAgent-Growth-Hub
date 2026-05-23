<template>
  <div class="change-password-page">
    <el-card shadow="never" class="change-password-card">
      <h1 class="page-title">修改密码</h1>
      <p class="page-subtitle">
        {{ authStore.mustChangePassword ? '首次登录须修改初始密码后方可使用系统' : '更新您的登录密码' }}
      </p>

      <el-form label-width="88px" @submit.prevent="handleSubmit">
        <el-form-item label="原密码" required>
          <el-input v-model="form.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" required>
          <el-input v-model="form.newPassword" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
        <el-form-item label="确认密码" required>
          <el-input v-model="form.confirmPassword" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
          <el-button v-if="!authStore.mustChangePassword" @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const handleSubmit = async () => {
  if (!form.oldPassword || !form.newPassword) {
    ElMessage.warning('请填写完整')
    return
  }
  if (form.newPassword.length < 8) {
    ElMessage.warning('新密码至少 8 位')
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  loading.value = true
  try {
    const user = await authApi.changePassword({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    authStore.setUser(user)
    ElMessage.success('密码已更新')
    await router.replace('/dashboard')
  } catch (e) {
    ElMessage.error(e instanceof Error ? e.message : '修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.change-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fc;
  padding: 24px;
}

.change-password-card {
  width: 100%;
  max-width: 480px;
}

.page-title {
  font-size: 22px;
  color: #1f2937;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: #9ca3af;
  margin-bottom: 24px;
  line-height: 1.6;
}
</style>
