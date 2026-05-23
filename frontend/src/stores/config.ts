import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ConfigItem } from '@/types'

const MOCK_CONFIGS: ConfigItem[] = [
  {
    id: '1',
    key: 'codeagent.portal_url',
    label: 'CodeAgent 门户地址',
    value: 'https://codeagent.example.com',
    category: '基础连接',
    description: '用户访问 CodeAgent 的主入口 URL',
    updatedAt: '2026-05-20 10:30:00',
    updatedBy: '管理员'
  },
  {
    id: '2',
    key: 'codeagent.usage.sync_interval',
    label: '使用数据同步间隔（分钟）',
    value: '30',
    category: '数据采集',
    description: '从 CodeAgent 拉取使用数据的 cron 间隔',
    updatedAt: '2026-05-18 14:00:00',
    updatedBy: '管理员'
  },
  {
    id: '3',
    key: 'notify.daily_report',
    label: '每日运营日报',
    value: 'true',
    category: '通知策略',
    description: '是否向运营群推送每日使用摘要',
    updatedAt: '2026-05-15 09:00:00',
    updatedBy: '管理员'
  }
]

export const useConfigStore = defineStore('config', () => {
  const items = ref<ConfigItem[]>([...MOCK_CONFIGS])
  const loading = ref(false)

  const fetchItems = async () => {
    loading.value = true
    try {
      // TODO: 替换为真实 API 调用
      await new Promise((resolve) => setTimeout(resolve, 300))
      items.value = [...MOCK_CONFIGS]
    } finally {
      loading.value = false
    }
  }

  const updateItem = async (id: string, payload: Partial<Pick<ConfigItem, 'value' | 'description'>>) => {
    loading.value = true
    try {
      await new Promise((resolve) => setTimeout(resolve, 200))
      const index = items.value.findIndex((item) => item.id === id)
      if (index === -1) return false

      items.value[index] = {
        ...items.value[index],
        ...payload,
        updatedAt: new Date().toLocaleString('zh-CN', { hour12: false }),
        updatedBy: '管理员'
      }
      return true
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    fetchItems,
    updateItem
  }
})
