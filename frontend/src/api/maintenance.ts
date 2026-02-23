import apiClient, { type ApiResponse } from './client'

export const maintenanceApi = {
  /** 儲存設定至 startup-config（write memory） */
  saveConfig: () =>
    apiClient.post<ApiResponse<null>>('/maintenance/save'),

  /** 取得 running-config */
  getRunningConfig: () =>
    apiClient.get<ApiResponse<string>>('/maintenance/config/running'),

  /** 取得 startup-config */
  getStartupConfig: () =>
    apiClient.get<ApiResponse<string>>('/maintenance/config/startup'),

  /** 取得 running 與 startup 的差異比對 */
  getConfigDiff: () =>
    apiClient.get<ApiResponse<string>>('/maintenance/config/diff'),

  /** 取得系統日誌 */
  getLogs: () =>
    apiClient.get<ApiResponse<string>>('/maintenance/logging'),

  /** 重啟設備 */
  reload: () =>
    apiClient.post<ApiResponse<null>>('/maintenance/reload'),
}
