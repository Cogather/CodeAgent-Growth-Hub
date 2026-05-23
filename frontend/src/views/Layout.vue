<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="22"><Monitor /></el-icon>
        </div>
        <span v-show="!isCollapsed" class="logo-text">{{ APP_NAME }}</span>
      </div>

      <div class="collapse-btn" @click="isCollapsed = !isCollapsed">
        <el-icon :size="16">
          <component :is="isCollapsed ? 'Expand' : 'Fold'" />
        </el-icon>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#f5f7fa"
        text-color="#374151"
        active-text-color="#6366f1"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-menu-item
          v-for="mod in APP_MODULES"
          :key="mod.key"
          :index="mod.path"
        >
          <el-icon><component :is="mod.icon" /></el-icon>
          <template #title>
            <span>{{ mod.title }}</span>
            <el-tag
              v-if="mod.status !== 'ready' && !isCollapsed"
              size="small"
              type="info"
              effect="plain"
              class="menu-tag"
            >
              {{ mod.status === 'developing' ? '开发中' : '待开发' }}
            </el-tag>
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="header-time">{{ currentTime }}</span>
          <el-dropdown @command="handleCommand">
            <div class="user-card">
              <div class="avatar">
                <el-icon><User /></el-icon>
              </div>
              <span class="username">{{ authStore.user?.name }}</span>
              <el-tag size="small" :type="authStore.isAdmin ? 'warning' : 'info'" effect="dark">
                {{ authStore.isAdmin ? '管理员' : '只读' }}
              </el-tag>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { APP_MODULES, APP_NAME } from '@/config/modules'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title as string | undefined)

const currentTime = ref('')
let timeInterval: number

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 60000)
})

onUnmounted(() => {
  clearInterval(timeInterval)
})

const handleCommand = async (command: string) => {
  if (command === 'changePassword') {
    await router.push('/change-password')
    return
  }
  if (command === 'logout') {
    await authStore.logout()
    await router.replace('/login')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.layout-aside {
  background: var(--hub-sidebar-bg);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.2s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.logo-text {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  display: flex;
  justify-content: flex-end;
  padding: 8px 12px;
  cursor: pointer;
  color: #9ca3af;
}

.collapse-btn:hover {
  color: #6366f1;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.menu-tag {
  margin-left: 6px;
  transform: scale(0.85);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, transparent 100%) !important;
  border-right: 3px solid #6366f1;
}

.layout-header {
  background: var(--hub-header-bg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #e5e7eb;
  height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-time {
  font-size: 13px;
  color: #9ca3af;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
}

.user-card:hover {
  background: #f3f4f6;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.username {
  font-size: 14px;
  color: #374151;
}

.dropdown-arrow {
  color: #9ca3af;
  font-size: 12px;
}

.layout-main {
  padding: 24px;
  background: var(--hub-page-bg);
  min-height: calc(100vh - 60px);
}
</style>
