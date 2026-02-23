import apiClient, { type ApiResponse } from './client'

export interface ConnectRequest {
  host: string
  username: string
  password: string
  secret?: string
}

export interface SessionStatus {
  connected: boolean
  has_unsaved_changes: boolean
  host: string | null
  username: string | null
}

export const authApi = {
  /** 建立 SSH 連線 */
  connect: (data: ConnectRequest) =>
    apiClient.post<ApiResponse<SessionStatus>>('/connect', data),

  /** 斷開 SSH 連線 */
  disconnect: () =>
    apiClient.post<ApiResponse<null>>('/disconnect'),

  /** 取得目前 Session 連線狀態 */
  getSessionStatus: () =>
    apiClient.get<ApiResponse<SessionStatus>>('/session/status'),
}
