import apiClient, { type ApiResponse } from './client'

export interface DeviceInfo {
  hostname: string
  model: string
  ios_version: string
  serial_number: string
  uptime: string
}

export interface InterfaceStatus {
  port: string
  name: string
  status: string
  vlan: string
  duplex: string
  speed: string
  type: string
  description: string
}

export const deviceApi = {
  /** 取得設備基本資訊 */
  getInfo: () =>
    apiClient.get<ApiResponse<DeviceInfo>>('/device/info'),

  /** 取得所有介面狀態（供面板使用） */
  getInterfaces: () =>
    apiClient.get<ApiResponse<InterfaceStatus[]>>('/device/interfaces'),

  /** 取得單一介面詳細資訊 */
  getInterface: (interfaceId: string) =>
    apiClient.get<ApiResponse<InterfaceStatus>>(`/device/interfaces/${interfaceId}`),
}
