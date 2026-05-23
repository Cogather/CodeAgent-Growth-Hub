import type { AppModule } from '@/types'

/**
 * 模块注册表 — 各模块负责人可在此登记模块信息，便于协作与导航展示。
 * 新增模块时：1) 在此添加条目  2) 在 router/index.ts 添加路由  3) 创建 views/{module}/index.vue
 */
export const APP_MODULES: AppModule[] = [
  {
    key: 'config',
    title: '配置中心',
    description: '组织架构、人员名单与黄/蓝/绿区网络权限配置',
    path: '/config',
    icon: 'Setting',
    owner: '核心团队',
    status: 'ready'
  },
  {
    key: 'usage',
    title: '使用统计',
    description: '用户使用 CodeAgent 的数据晾晒与统计分析',
    path: '/usage',
    icon: 'DataLine',
    status: 'ready'
  },
  {
    key: 'issues',
    title: '12345 问题统计',
    description: '12345 渠道问题收集、分类与统计',
    path: '/issues',
    icon: 'Warning',
    status: 'planned'
  },
  {
    key: 'practices',
    title: '优秀实践',
    description: '优秀实践案例的收集、审核与推广看护',
    path: '/practices',
    icon: 'Star',
    status: 'planned'
  },
  {
    key: 'expertise',
    title: '专家经验',
    description: '专家经验数据的录入、看护与晾晒统计',
    path: '/expertise',
    icon: 'Reading',
    status: 'planned'
  }
]

export const APP_NAME = 'CodeAgent 运营中枢'
export const APP_SUBTITLE = '推广使用情况运营运维辅助平台'
