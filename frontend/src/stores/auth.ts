import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>({
    id: 1,
    username: 'admin',
    name: '管理员',
    department: '运营组',
    role: 'admin'
  })

  const isAdmin = computed(() => user.value?.role === 'admin')

  const setUser = (newUser: User | null) => {
    user.value = newUser
  }

  return {
    user,
    isAdmin,
    setUser
  }
})
