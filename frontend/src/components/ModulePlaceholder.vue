<template>
  <div class="module-placeholder">
    <el-card shadow="never" class="placeholder-card">
      <div class="placeholder-icon">
        <el-icon :size="48"><component :is="icon" /></el-icon>
      </div>
      <h2>{{ title }}</h2>
      <p class="description">{{ description }}</p>

      <el-tag :type="statusTagType" effect="plain" class="status-tag">
        {{ statusLabel }}
      </el-tag>

      <div class="hint-box">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ hint }}</span>
      </div>

      <div v-if="owner" class="owner">
        模块负责人：<strong>{{ owner }}</strong>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ModuleStatus } from '@/types'

const props = withDefaults(
  defineProps<{
    title: string
    description: string
    icon?: string
    status?: ModuleStatus
    owner?: string
    hint?: string
  }>(),
  {
    icon: 'Box',
    status: 'planned',
    hint: '该模块页面骨架已就绪，请在 views/{module}/index.vue 中实现具体功能。'
  }
)

const statusLabel = computed(() => {
  const map: Record<ModuleStatus, string> = {
    ready: '已上线',
    developing: '开发中',
    planned: '待开发'
  }
  return map[props.status]
})

const statusTagType = computed(() => {
  const map: Record<ModuleStatus, 'success' | 'warning' | 'info'> = {
    ready: 'success',
    developing: 'warning',
    planned: 'info'
  }
  return map[props.status]
})
</script>

<style scoped>
.module-placeholder {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.placeholder-card {
  max-width: 560px;
  width: 100%;
  text-align: center;
  padding: 48px 32px;
}

.placeholder-icon {
  width: 88px;
  height: 88px;
  margin: 0 auto 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

h2 {
  font-size: 22px;
  color: #1f2937;
  margin-bottom: 12px;
}

.description {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.status-tag {
  margin-bottom: 24px;
}

.hint-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  text-align: left;
  padding: 14px 16px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.hint-box .el-icon {
  margin-top: 2px;
  color: #9ca3af;
  flex-shrink: 0;
}

.owner {
  margin-top: 20px;
  font-size: 13px;
  color: #9ca3af;
}

.owner strong {
  color: #6366f1;
}
</style>
