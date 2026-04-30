import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/personnel/list',
    children: [
      {
        path: '/personnel/organization',
        name: 'PersonnelOrganization',
        component: () => import('@/views/personnel/organization.vue'),
        meta: { title: '组织架构管理', icon: 'OfficeBuilding', role: 'admin' }
      },
      {
        path: '/personnel/list',
        name: 'PersonnelList',
        component: () => import('@/views/personnel/personnel.vue'),
        meta: { title: '人员名单', icon: 'User', role: 'admin' }
      },
      {
        path: '/personnel/permission',
        name: 'PersonnelPermission',
        component: () => import('@/views/personnel/permission.vue'),
        meta: { title: '权限管理', icon: 'Key', role: 'admin' }
      },
      {
        path: '/personnel/usage',
        name: 'PersonnelUsage',
        component: () => import('@/views/personnel/usage.vue'),
        meta: { title: '使用数据', icon: 'Histogram', role: 'admin' }
      },
      {
        path: '/personnel/summary',
        name: 'PersonnelSummary',
        component: () => import('@/views/personnel/summary.vue'),
        meta: { title: '数据汇总', icon: 'DataAnalysis', role: 'admin' }
      },
      {
        path: '/personnel/audit-logs',
        name: 'PersonnelAuditLogs',
        component: () => import('@/views/personnel/audit-logs.vue'),
        meta: { title: '变更日志', icon: 'Document', role: 'admin' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const metaRole = to.meta.role as string | undefined
  
  if (metaRole && metaRole === 'admin' && authStore.user?.role !== 'admin') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
