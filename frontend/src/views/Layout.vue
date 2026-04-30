<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '220px'">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="24"><MagicStick /></el-icon>
        </div>
        <span v-show="!isCollapsed" class="logo-text">CodeAgent试点指挥中心</span>
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
        <el-sub-menu index="/personnel" v-if="isAdmin">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>人员管理</span>
          </template>
          <el-menu-item index="/personnel/organization">组织架构管理</el-menu-item>
          <el-menu-item index="/personnel/list">人员名单</el-menu-item>
          <el-menu-item index="/personnel/permission">权限管理</el-menu-item>
          <el-menu-item index="/personnel/usage">使用数据</el-menu-item>
          <el-menu-item index="/personnel/summary">数据汇总</el-menu-item>
          <el-menu-item index="/personnel/audit-logs">变更日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-if="currentRoute">{{ currentRoute }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <div class="header-time">{{ currentTime }}</div>
          <el-dropdown @command="handleCommand">
            <div class="user-card">
              <div class="avatar">
                <el-icon><User /></el-icon>
              </div>
              <span class="username">{{ authStore.user?.name }}</span>
              <el-tag size="small" :type="isAdmin ? 'warning' : 'info'" effect="dark">
                {{ isAdmin ? '管理员' : '普通用户' }}
              </el-tag>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="switchAdmin">切换为管理员</el-dropdown-item>
                <el-dropdown-item command="switchUser">切换为普通用户</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)

const isAdmin = computed(() => authStore.isAdmin)
const activeMenu = computed(() => route.path)

const currentRoute = computed(() => {
  const meta = route.meta
  return meta.title as string
})

const currentTime = ref('')
let timeInterval: number

const updateTime = () => {
  const now = new Date()
  currentTime.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 60000)
})

onUnmounted(() => {
  clearInterval(timeInterval)
})

const handleCommand = (command: string) => {
  if (command === 'switchAdmin') {
    authStore.setUser({ ...authStore.user!, role: 'admin' })
  } else if (command === 'switchUser') {
    authStore.setUser({ ...authStore.user!, role: 'user' })
  } else if (command === 'logout') {
    router.push('/')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background: linear-gradient(180deg, #f5f7fa 0%, #eef2f5 100%);
  overflow-x: hidden;
  transition: width 0.3s ease;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid rgba(99, 102, 241, 0.15);
  background: rgba(99, 102, 241, 0.08);
  padding: 0 10px;
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
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  flex-shrink: 0;
}

.logo-text {
  white-space: nowrap;
  color: #1f2937;
  font-weight: 600;
  font-size: 15px;
}

.collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  cursor: pointer;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s;
  background: rgba(99, 102, 241, 0.05);
}

.collapse-btn:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  transition: all 0.3s;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background: rgba(99, 102, 241, 0.1) !important;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, transparent 100%) !important;
  border-right: 3px solid #6366f1;
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #6366f1 !important;
}

.el-header {
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-time {
  font-size: 13px;
  color: #9ca3af;
  padding: 6px 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.user-card:hover {
  background: #f3f4f6;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.dropdown-arrow {
  color: #9ca3af;
  font-size: 12px;
}

.el-main {
  padding: 24px;
  background: #f8f9fc;
  min-height: calc(100vh - 60px);
}
</style>
