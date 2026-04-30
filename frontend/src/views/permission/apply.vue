<template>
  <div class="apply-page">
    <div class="page-header">
      <div class="page-title">
        <h2>权限申请</h2>
        <p>提交权限申请，为团队成员开通AI工具使用权限</p>
      </div>
    </div>

    <el-card class="apply-card" shadow="never">
      <el-tabs v-model="activeTab" class="apply-tabs">
        <el-tab-pane label="单账号申请" name="single">
          <div class="form-container">
            <el-form :model="singleForm" label-position="top" class="apply-form">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="工号" required>
                    <el-input 
                      v-model="singleForm.username" 
                      placeholder="请输入6位工号"
                      size="large"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="网络区域" required>
                    <el-select v-model="singleForm.zone" placeholder="请选择网络区域" size="large" style="width: 100%">
                      <el-option label="🌐 黄区" value="yellow" />
                      <el-option label="🌐 蓝区" value="blue" />
                      <el-option label="🌐 绿区" value="green" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="工具" required>
                    <el-select v-model="singleForm.tool" placeholder="请选择工具" size="large" style="width: 100%">
                      <el-option v-for="t in mockDataStore.tools" :key="t" :label="t" :value="t" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="模型" required>
                    <el-select v-model="singleForm.model" placeholder="请选择模型" size="large" style="width: 100%">
                      <el-option v-for="m in mockDataStore.models" :key="m" :label="m" :value="m" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item>
                <el-button type="primary" size="large" @click="submitSingle" class="submit-btn">
                  <el-icon><Plus /></el-icon>
                  提交申请
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="批量申请" name="batch">
          <div class="form-container">
            <div class="batch-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>支持批量输入工号，系统会自动去重和校验格式</span>
            </div>
            <el-form :model="batchForm" label-position="top" class="apply-form">
              <el-form-item label="工号列表" required>
                <el-input
                  v-model="batchForm.usernames"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入工号，每行一个，支持逗号、空格分隔&#10;示例：100001, 100002, 100003"
                  size="large"
                />
                <div class="username-stats">
                  <div class="stat-item valid">
                    <el-icon><CircleCheckFilled /></el-icon>
                    <span>有效: {{ validCount }}</span>
                  </div>
                  <div class="stat-item duplicate">
                    <el-icon><WarningFilled /></el-icon>
                    <span>重复: {{ duplicateCount }}</span>
                  </div>
                  <div class="stat-item invalid">
                    <el-icon><CircleCloseFilled /></el-icon>
                    <span>无效: {{ invalidCount }}</span>
                  </div>
                </div>
              </el-form-item>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="网络区域" required>
                    <el-select v-model="batchForm.zone" placeholder="请选择网络区域" size="large" style="width: 100%">
                      <el-option label="🌐 黄区" value="yellow" />
                      <el-option label="🌐 蓝区" value="blue" />
                      <el-option label="🌐 绿区" value="green" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="工具" required>
                    <el-select v-model="batchForm.tool" placeholder="请选择工具" size="large" style="width: 100%">
                      <el-option v-for="t in mockDataStore.tools" :key="t" :label="t" :value="t" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="模型" required>
                    <el-select v-model="batchForm.model" placeholder="请选择模型" size="large" style="width: 100%">
                      <el-option v-for="m in mockDataStore.models" :key="m" :label="m" :value="m" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item>
                <el-button type="success" size="large" @click="submitBatch" :disabled="validCount === 0" class="submit-btn">
                  <el-icon><Plus /></el-icon>
                  批量提交 ({{ validCount }} 个工号)
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useMockDataStore } from '@/stores/mockData'
import { useAuthStore } from '@/stores/auth'
import type { ZoneType } from '@/types'

const mockDataStore = useMockDataStore()
const authStore = useAuthStore()

const activeTab = ref('single')

const singleForm = reactive({
  username: '',
  zone: '' as ZoneType | '',
  tool: '',
  model: ''
})

const batchForm = reactive({
  usernames: '',
  zone: '' as ZoneType | '',
  tool: '',
  model: ''
})

const parseUsernames = (input: string) => {
  const list = input.split(/[\n,，\s]+/).filter(Boolean)
  const unique = [...new Set(list)]
  const valid = unique.filter(u => /^\d{5,6}$/.test(u))
  const invalid = unique.filter(u => !/^\d{5,6}$/.test(u))
  const duplicate = unique.length - valid.length - invalid.length
  
  return { valid, invalid, duplicate, total: unique.length }
}

const usernameStats = computed(() => parseUsernames(batchForm.usernames))
const validCount = computed(() => usernameStats.value.valid.length)
const invalidCount = computed(() => usernameStats.value.invalid.length + usernameStats.value.duplicate)

const duplicateCount = computed(() => {
  const list = batchForm.usernames.split(/[\n,，\s]+/).filter(Boolean)
  const unique = [...new Set(list)]
  return list.length - unique.length
})

const submitSingle = () => {
  if (!singleForm.username || !singleForm.zone || !singleForm.tool || !singleForm.model) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  if (!/^\d{5,6}$/.test(singleForm.username)) {
    ElMessage.error('工号格式不正确')
    return
  }
  
  mockDataStore.addAccessRequest({
    zone: singleForm.zone as ZoneType,
    tool: singleForm.tool,
    model: singleForm.model,
    status: 'pending',
    submitter: authStore.user?.username || '',
    submitterName: authStore.user?.name || '',
    accounts: [{ id: Date.now(), requestId: 0, username: singleForm.username, status: 'pending' }]
  })
  
  ElMessage.success('提交成功')
  singleForm.username = ''
  singleForm.zone = ''
  singleForm.tool = ''
  singleForm.model = ''
}

const submitBatch = () => {
  if (!batchForm.zone || !batchForm.tool || !batchForm.model) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  const { valid } = usernameStats.value
  if (valid.length === 0) {
    ElMessage.warning('请输入有效的工号')
    return
  }
  
  const accounts = valid.map((username, idx) => ({
    id: Date.now() + idx,
    requestId: 0,
    username,
    status: 'pending' as const
  }))
  
  mockDataStore.addAccessRequest({
    zone: batchForm.zone as ZoneType,
    tool: batchForm.tool,
    model: batchForm.model,
    status: 'pending',
    submitter: authStore.user?.username || '',
    submitterName: authStore.user?.name || '',
    accounts
  })
  
  ElMessage.success(`成功提交 ${valid.length} 个工号`)
  batchForm.usernames = ''
  batchForm.zone = ''
  batchForm.tool = ''
  batchForm.model = ''
}
</script>

<style scoped>
.apply-page {
  max-width: 900px;
}

.page-header {
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

.apply-card {
  border: none;
  border-radius: 16px;
}

.apply-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.apply-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

.apply-tabs :deep(.el-tabs__item.is-active) {
  color: #6366f1;
}

.apply-tabs :deep(.el-tabs__active-bar) {
  background-color: #6366f1;
}

.form-container {
  max-width: 700px;
}

.batch-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 10px;
  color: #0369a1;
  font-size: 14px;
  margin-bottom: 20px;
}

.apply-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
}

.username-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 20px;
}

.stat-item.valid {
  background: #ecfdf5;
  color: #059669;
}

.stat-item.duplicate {
  background: #fffbeb;
  color: #d97706;
}

.stat-item.invalid {
  background: #fef2f2;
  color: #dc2626;
}

.submit-btn {
  padding: 12px 32px;
  font-weight: 500;
}
</style>
