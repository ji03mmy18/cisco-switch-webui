import axios from 'axios'

/** 統一 API 回傳格式 */
export interface ApiResponse<T = unknown> {
  success: boolean
  data: T | null
  message: string
}

/** 統一的 Axios 實例，所有 API 模組共用 */
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient
