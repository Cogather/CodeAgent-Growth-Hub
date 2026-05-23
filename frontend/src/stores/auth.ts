import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/auth'
import type { AuthUser } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const initialized = ref(false)

  const isAdmin = computed(() => user.value?.role === 'admin')
  const mustChangePassword = computed(() => user.value?.must_change_password === true)

  async function fetchMe() {
    try {
      user.value = await authApi.me()
    } catch {
      user.value = null
    } finally {
      initialized.value = true
    }
  }

  async function login(username: string, password: string) {
    user.value = await authApi.login({ username, password })
  }

  async function logout() {
    await authApi.logout()
    user.value = null
  }

  function setUser(newUser: AuthUser | null) {
    user.value = newUser
  }

  return {
    user,
    initialized,
    isAdmin,
    mustChangePassword,
    fetchMe,
    login,
    logout,
    setUser
  }
})
