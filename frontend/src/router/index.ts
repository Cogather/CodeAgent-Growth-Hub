import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/change-password/index.vue'),
    meta: { requiresAuth: true, allowMustChange: true, title: '修改密码' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      },
      {
        path: '/config',
        name: 'Config',
        component: () => import('@/views/config/index.vue'),
        meta: { title: '配置中心', icon: 'Setting', module: 'config' }
      },
      {
        path: '/usage',
        name: 'Usage',
        component: () => import('@/views/usage/index.vue'),
        meta: { title: '使用统计', icon: 'DataLine', module: 'usage' }
      },
      {
        path: '/issues',
        name: 'Issues',
        component: () => import('@/views/issues/index.vue'),
        meta: { title: '12345 问题统计', icon: 'Warning', module: 'issues' }
      },
      {
        path: '/practices',
        name: 'Practices',
        component: () => import('@/views/practices/index.vue'),
        meta: { title: '优秀实践', icon: 'Star', module: 'practices' }
      },
      {
        path: '/expertise',
        name: 'Expertise',
        component: () => import('@/views/expertise/index.vue'),
        meta: { title: '专家经验', icon: 'Reading', module: 'expertise' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.fetchMe()
  }

  const isPublic = to.meta.public === true
  const allowMustChange = to.meta.allowMustChange === true

  if (isPublic) {
    if (auth.user && to.path === '/login') {
      return auth.mustChangePassword ? '/change-password' : '/dashboard'
    }
    return true
  }

  if (to.meta.requiresAuth !== false && !auth.user) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (auth.user && auth.mustChangePassword && !allowMustChange) {
    return '/change-password'
  }

  return true
})

export default router
