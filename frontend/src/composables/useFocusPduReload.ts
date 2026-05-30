import { onMounted, onUnmounted } from 'vue'

/** 顶栏 PDU 视角开关变化或关注列表变更时刷新当前页数据 */
export function useFocusPduReload(reload: () => void | Promise<void>) {
  const handler = () => {
    void reload()
  }

  onMounted(() => {
    window.addEventListener('focus-pdu-changed', handler)
  })

  onUnmounted(() => {
    window.removeEventListener('focus-pdu-changed', handler)
  })
}
