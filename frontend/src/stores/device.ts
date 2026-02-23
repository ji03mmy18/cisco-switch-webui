import { defineStore } from 'pinia'
import { ref } from 'vue'
import { deviceApi, type DeviceInfo, type InterfaceStatus } from '@/api/device'

export const useDeviceStore = defineStore('device', () => {
  const deviceInfo = ref<DeviceInfo | null>(null)
  const interfaces = ref<InterfaceStatus[]>([])
  const isLoadingInterfaces = ref(false)
  const lastUpdated = ref<Date | null>(null)

  /** 取得設備基本資訊 */
  async function fetchDeviceInfo() {
    const res = await deviceApi.getInfo()
    if (res.data.success && res.data.data) {
      deviceInfo.value = res.data.data
    }
    return res.data
  }

  /** 取得所有介面狀態（供面板輪詢使用） */
  async function fetchInterfaces() {
    isLoadingInterfaces.value = true
    try {
      const res = await deviceApi.getInterfaces()
      if (res.data.success && res.data.data) {
        interfaces.value = res.data.data
        lastUpdated.value = new Date()
      }
      return res.data
    } finally {
      isLoadingInterfaces.value = false
    }
  }

  /** 重置所有設備資料（登出時呼叫） */
  function reset() {
    deviceInfo.value = null
    interfaces.value = []
    lastUpdated.value = null
  }

  return {
    deviceInfo,
    interfaces,
    isLoadingInterfaces,
    lastUpdated,
    fetchDeviceInfo,
    fetchInterfaces,
    reset,
  }
})
