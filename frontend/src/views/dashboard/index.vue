<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1>工作台</h1>
        <p>{{ APP_SUBTITLE }}</p>
      </div>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ APP_MODULES.length }}</div>
          <div class="stat-label">规划模块</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ readyCount }}</div>
          <div class="stat-label">已上线</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ developingCount }}</div>
          <div class="stat-label">开发中</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ plannedCount }}</div>
          <div class="stat-label">待开发</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="module-grid-card">
      <template #header>
        <span class="card-title">功能模块</span>
      </template>
      <el-row :gutter="16">
        <el-col
          v-for="mod in APP_MODULES"
          :key="mod.key"
          :xs="24"
          :sm="12"
          :lg="8"
          class="module-col"
        >
          <div class="module-card" @click="goToModule(mod.path)">
            <div class="module-card-header">
              <div class="module-icon">
                <el-icon :size="22"><component :is="mod.icon" /></el-icon>
              </div>
              <el-tag :type="statusType(mod.status)" size="small" effect="plain">
                {{ statusText(mod.status) }}
              </el-tag>
            </div>
            <h3>{{ mod.title }}</h3>
            <p>{{ mod.description }}</p>
            <div v-if="mod.owner" class="module-owner">负责人：{{ mod.owner }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { APP_MODULES, APP_SUBTITLE } from '@/config/modules'
import type { ModuleStatus } from '@/types'

const router = useRouter()

const readyCount = computed(() => APP_MODULES.filter((m) => m.status === 'ready').length)
const developingCount = computed(() => APP_MODULES.filter((m) => m.status === 'developing').length)
const plannedCount = computed(() => APP_MODULES.filter((m) => m.status === 'planned').length)

const statusText = (status: ModuleStatus) => {
  const map: Record<ModuleStatus, string> = {
    ready: '已上线',
    developing: '开发中',
    planned: '待开发'
  }
  return map[status]
}

const statusType = (status: ModuleStatus) => {
  const map: Record<ModuleStatus, 'success' | 'warning' | 'info'> = {
    ready: 'success',
    developing: 'warning',
    planned: 'info'
  }
  return map[status]
}

const goToModule = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-header h1 {
  font-size: 24px;
  color: #1f2937;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 14px;
  color: #9ca3af;
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 8px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #6366f1;
}

.stat-label {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
}

.card-title {
  font-weight: 600;
  color: #374151;
}

.module-col {
  margin-bottom: 16px;
}

.module-card {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  height: 100%;
}

.module-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

.module-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.module-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.module-card h3 {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 8px;
}

.module-card p {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.module-owner {
  margin-top: 12px;
  font-size: 12px;
  color: #9ca3af;
}
</style>
