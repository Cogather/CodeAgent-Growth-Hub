import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
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
        path: '/audit',
        name: 'Audit',
        component: () => import('@/views/audit/index.vue'),
        meta: { title: '变更记录', icon: 'Document', module: 'audit' }
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

export default router
