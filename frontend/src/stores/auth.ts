import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>({
    id: 1,
    username: 'admin',
    name: '管理员',
    department: '研发部',
    role: 'admin'
  })

  const isAdmin = ref(true)

  const setUser = (newUser: User | null) => {
    user.value = newUser
    isAdmin.value = newUser?.role === 'admin'
  }

  return {
    user,
    isAdmin,
    setUser
  }
})
