import type {
  SysUserCreatePayload,
  SysUserCreateResponse,
  SysUserItem,
  SysUserListResponse,
  SysUserResetPasswordResponse,
  SysUserUpdatePayload
} from '@/types'
import { requestJson } from '@/api/client'

export const usersApi = {
  list: () => requestJson<SysUserListResponse>('/users'),

  create: (payload: SysUserCreatePayload) =>
    requestJson<SysUserCreateResponse>('/users', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  update: (userId: number, payload: SysUserUpdatePayload) =>
    requestJson<SysUserItem>(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    }),

  resetPassword: (userId: number) =>
    requestJson<SysUserResetPasswordResponse>(`/users/${userId}/reset-password`, {
      method: 'POST'
    })
}
