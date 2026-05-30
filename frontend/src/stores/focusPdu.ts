import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { focusPduApi } from '@/api/focusPdu'
import type { FocusPduItem } from '@/types'

const STORAGE_KEY = 'focus_pdu_perspective_enabled'

export const useFocusPduStore = defineStore('focusPdu', () => {
  const enabled = ref(localStorage.getItem(STORAGE_KEY) === '1')
  const items = ref<FocusPduItem[]>([])
  const targetDepth = ref(4)
  const loading = ref(false)
  const loaded = ref(false)

  const label = computed(() => {
    if (items.value.length === 0) return 'PDU 视角'
    const names = items.value.map((item) => item.alias || item.name)
    if (names.length <= 2) return `PDU：${names.join('、')}`
    return `PDU：${names.slice(0, 2).join('、')} 等 ${names.length} 个`
  })

  async function fetchList() {
    loading.value = true
    try {
      const data = await focusPduApi.list()
      items.value = data.items
      targetDepth.value = data.target_depth
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  function setEnabled(next: boolean) {
    enabled.value = next
    localStorage.setItem(STORAGE_KEY, next ? '1' : '0')
  }

  function displayName(item: FocusPduItem) {
    return item.alias || item.name
  }

  return {
    enabled,
    items,
    targetDepth,
    loading,
    loaded,
    label,
    fetchList,
    setEnabled,
    displayName
  }
})
