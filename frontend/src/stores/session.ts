import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type ConnectRequest } from '@/api/auth'

export const useSessionStore = defineStore('session', () => {
  const isConnected = ref(false)
  const hasUnsavedChanges = ref(false)
  const host = ref<string | null>(null)
  const username = ref<string | null>(null)
  /** 是否已向後端確認過連線狀態（用於路由守衛） */
  const initialized = ref(false)

  /** 向後端確認目前連線狀態 */
  async function checkStatus() {
    try {
      const res = await authApi.getSessionStatus()
      const data = res.data.data
      if (res.data.success && data) {
        isConnected.value = data.connected
        hasUnsavedChanges.value = data.has_unsaved_changes
        host.value = data.host
        username.value = data.username
      }
    } catch {
      isConnected.value = false
    } finally {
      initialized.value = true
    }
  }

  /** 登入：建立 SSH 連線 */
  async function login(credentials: ConnectRequest) {
    const res = await authApi.connect(credentials)
    if (res.data.success && res.data.data) {
      isConnected.value = true
      hasUnsavedChanges.value = false
      host.value = credentials.host
      username.value = credentials.username
    }
    return res.data
  }

  /** 登出：斷開 SSH 連線並重置狀態 */
  async function logout() {
    await authApi.disconnect()
    isConnected.value = false
    hasUnsavedChanges.value = false
    host.value = null
    username.value = null
  }

  /** 標記有未儲存的變更 */
  function markChanged() {
    hasUnsavedChanges.value = true
  }

  /** 標記已儲存 */
  function markSaved() {
    hasUnsavedChanges.value = false
  }

  return {
    isConnected,
    hasUnsavedChanges,
    host,
    username,
    initialized,
    checkStatus,
    login,
    logout,
    markChanged,
    markSaved,
  }
})
