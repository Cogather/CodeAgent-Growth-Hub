import type { AuthUser, ChangePasswordPayload, LoginPayload } from '@/types'
import { requestJson } from '@/api/client'

export const authApi = {
  login: (payload: LoginPayload) =>
    requestJson<AuthUser>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  logout: () => requestJson<void>('/auth/logout', { method: 'POST' }),

  me: () => requestJson<AuthUser>('/auth/me'),

  changePassword: (payload: ChangePasswordPayload) =>
    requestJson<AuthUser>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
}
