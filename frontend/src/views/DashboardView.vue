<template>
  <el-config-provider :locale="zhTw">
    <div class="dashboard">
      <!-- 頂部導航列 -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="device-name">{{ deviceStore.deviceInfo?.hostname ?? '載入中...' }}</span>
          <el-tag type="info" size="small" class="device-model">
            {{ deviceStore.deviceInfo?.model ?? 'WS-C2960X-48TS-L' }}
          </el-tag>
          <span v-if="deviceStore.deviceInfo?.uptime" class="uptime">
            已運行 {{ deviceStore.deviceInfo.uptime }}
          </span>
        </div>

        <div class="topbar-right">
          <!-- 未儲存變更提示 -->
          <el-tag
            v-if="sessionStore.hasUnsavedChanges"
            type="warning"
            effect="dark"
            class="unsaved-badge"
          >
            ⚠ 有未儲存的變更
          </el-tag>
          <el-tag v-else type="success" effect="plain" class="unsaved-badge">
            已儲存
          </el-tag>

          <!-- 儲存設定按鈕 -->
          <el-button
            type="primary"
            size="small"
            :disabled="!sessionStore.hasUnsavedChanges"
            @click="handleSave"
          >
            儲存設定
          </el-button>

          <!-- 登出按鈕 -->
          <el-button size="small" @click="handleLogout">登出</el-button>
        </div>
      </header>

      <!-- 主要內容分頁 -->
      <main class="main-content">
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="Port 面板" name="ports">
            <div class="tab-placeholder">
              <!-- SwitchPanel 元件將在此實作 -->
              <el-empty description="Port 面板開發中" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="全域安全設定" name="security">
            <div class="tab-placeholder">
              <el-empty description="全域安全設定開發中" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="IP/MAC 綁定" name="bindings">
            <div class="tab-placeholder">
              <el-empty description="IP/MAC 綁定管理開發中" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="ARP 檢查" name="arp">
            <div class="tab-placeholder">
              <el-empty description="ARP 檢查開發中" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="網路資訊" name="network">
            <div class="tab-placeholder">
              <el-empty description="網路資訊開發中" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="維護管理" name="maintenance">
            <div class="tab-placeholder">
              <el-empty description="維護管理開發中" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import zhTw from 'element-plus/dist/locale/zh-tw.mjs'
import { useSessionStore } from '@/stores/session'
import { useDeviceStore } from '@/stores/device'
import { maintenanceApi } from '@/api/maintenance'

const router = useRouter()
const sessionStore = useSessionStore()
const deviceStore = useDeviceStore()

const activeTab = ref('ports')

// 定時輪詢介面狀態（每 30 秒）
let pollingTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  // 載入設備基本資訊
  await deviceStore.fetchDeviceInfo()
  // 首次載入介面狀態
  await deviceStore.fetchInterfaces()
  // 啟動定時輪詢
  pollingTimer = setInterval(() => {
    deviceStore.fetchInterfaces()
  }, 30000)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})

/** 儲存設定 */
async function handleSave() {
  try {
    const res = await maintenanceApi.saveConfig()
    if (res.data.success) {
      sessionStore.markSaved()
      ElMessage.success('設定已成功儲存')
    } else {
      ElMessage.error(res.data.message)
    }
  } catch {
    ElMessage.error('儲存失敗，請重試')
  }
}

/** 登出（有未儲存變更時顯示確認 Dialog） */
async function handleLogout() {
  if (sessionStore.hasUnsavedChanges) {
    const action = await ElMessageBox.confirm(
      '您有尚未儲存的設定變更，是否要儲存後再登出？',
      '未儲存的變更',
      {
        distinguishCancelAndClose: true,
        confirmButtonText: '儲存並登出',
        cancelButtonText: '不儲存直接登出',
        type: 'warning',
      },
    ).catch((action: string) => action)

    if (action === 'confirm') {
      await handleSave()
    } else if (action === 'cancel') {
      // 不儲存直接登出
    } else {
      // 使用者點擊 X 關閉，取消登出
      return
    }
  }

  await sessionStore.logout()
  deviceStore.reset()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.device-model {
  font-family: monospace;
}

.uptime {
  font-size: 12px;
  color: #909399;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.unsaved-badge {
  font-size: 12px;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.tab-placeholder {
  padding: 40px 0;
}
</style>
