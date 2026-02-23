# Cisco Switch Web Management Interface

## 專案概述

開發一組網頁應用程式，作為 Cisco 交換器的代理操作介面。後端透過 SSH 與交換器通訊，前端提供視覺化的管理介面，取代傳統 SSH 工具的操作方式。

## 目標設備

- **型號：** Cisco WS-C2960X-48TS-L
- **埠配置：** 48 x GbE RJ45 + 4 x SFP Uplink
- **面板排列：** RJ45 上排奇數 (1,3,5,...,47)、下排偶數 (2,4,6,...,48)，SFP 在右側
- **層級：** Layer 2 交換器
- **作業系統：** Cisco IOS

## 技術架構

### 後端

- **語言：** Python
- **框架：** FastAPI
- **SSH 通訊：** Netmiko（device_type: `cisco_ios`）
- **CLI 輸出解析：** TextFSM / NTC Templates
- **API 風格：** RESTful

### 前端

- **框架：** Vue 3（使用 Vite 建構）
- **元件庫：** Element Plus（按需引入，搭配 unplugin-vue-components 與 unplugin-auto-import）
- **狀態管理：** Pinia
- **路由：** Vue Router
- **語言：** 元件內建文字使用中文（需設定 ElConfigProvider 中文語言包）

---

## 核心功能需求

### 1. 登入與連線管理

- 首頁為登入頁面，使用者輸入交換器的連線資訊：
  - Host / IP
  - Username
  - Password
  - Enable Password（選填）
- 登入後建立 SSH 連線，後續操作透過此連線執行
- 提供登出功能

### 2. 視覺化 Port 面板（核心 UI）

參考 UniFi 管理介面的設計風格，以圖形化方式呈現交換器的實體面板：

- 使用 CSS Grid / Flexbox 排列，還原 WS-C2960X-48TS-L 的實體埠位配置
- 每個 Port 為獨立的 Vue 元件
- **顏色邏輯：**
  - 綠色 — GbE 連線中 (1000Mbps)
  - 黃綠色 — Fast Ethernet 連線中 (100Mbps)
  - 灰色 — 未連線（up 但 no link）
  - 深灰 / 空心 — 管理性關閉 (shutdown)
- **Hover 互動：** 滑鼠懸停顯示 Tooltip/Popover，內容包含介面名稱、description、速率、雙工模式、流量統計
- **點擊互動：** 點擊 Port 展開該 Port 的詳細資訊與操作面板（含 IPSG、MAC Verify 開關等設定）
- **定時輪詢：** 每 30 秒更新面板狀態
- **資料來源：** `show interfaces status`，解析後回傳 JSON

### 3. Port 安全設定（By Port）

此為本專案的主要需求，所有設定均以單一 Port 為操作單位：

#### 3.1 IPSG（IP Source Guard）開關

- 對應指令：`ip verify source`
- 以 Switch 元件呈現開/關狀態
- 前置條件檢查：該 Port 所屬 VLAN 必須已啟用 DHCP Snooping，否則顯示警示

#### 3.2 MAC Verify 開關

- 對應指令：`ip verify source port-security`
- 以 Switch 元件呈現開/關狀態
- 前置條件檢查：
  - DHCP Snooping 必須已啟用
  - 該 Port 的 Port Security 必須已啟用
  - 若前置條件未滿足，介面需明確提示並引導使用者完成前置設定

#### 3.3 IP/MAC 靜態綁定管理

- 對應指令：`ip source binding <mac> vlan <vlan-id> <ip> interface <interface>`
- 提供新增綁定的表單（輸入欄位：MAC Address、IP Address、VLAN ID、Interface）
- 以表格顯示目前所有綁定條目（`show ip source binding`），支援搜尋與篩選
- 表格列上提供刪除按鈕

#### 3.4 ARP 表查詢

- 顯示 ARP Inspection 綁定資訊（`show ip arp inspection bindings`）
- 顯示 ARP Inspection 統計數據（`show ip arp inspection statistics`）
- 支援搜尋與篩選

### 4. 全域狀態總覽

在獨立分頁中顯示以下全域資訊，作為所有安全功能的前置條件檢查：

- DHCP Snooping 啟用狀態
- DHCP Snooping 啟用的 VLAN 列表
- DHCP Snooping 信任介面列表
- 若 DHCP Snooping 未啟用，其他相關功能頁面需顯示明確警示

### 5. 監控與查詢功能

| 功能 | 對應指令 | 說明 |
|------|---------|------|
| 介面狀態 | `show interfaces status` | Port 的 up/down、速率、雙工、VLAN |
| VLAN 資訊 | `show vlan brief` | VLAN 列表及所屬 Port |
| MAC Address Table | `show mac address-table` | MAC 與 Port 對應，支援搜尋 |
| CDP 鄰居 | `show cdp neighbors detail` | 相鄰設備資訊 |
| 設備資訊 | `show version` | 型號、IOS 版本、Uptime、序號 |
| 介面流量統計 | `show interfaces counters` | 收發封包數、錯誤數 |
| Spanning Tree | `show spanning-tree` | STP 根橋、Port 角色與狀態 |
| Port Security | `show port-security` | Port Security 啟用狀態、違規次數 |
| 系統日誌 | `show logging` | 日誌內容，支援篩選與搜尋 |

### 6. 設定操作功能

| 功能 | 說明 |
|------|------|
| 介面開關 | 對 Port 執行 shutdown / no shutdown，需二次確認 |
| VLAN 管理 | 新增/刪除 VLAN，修改 Port 的 VLAN 歸屬（access/trunk） |
| Port 基本設定 | 速率、雙工模式、description |
| Port Security 設定 | 啟用/停用、最大 MAC 數、違規動作 |

### 7. 維護管理功能

| 功能 | 說明 |
|------|------|
| 儲存設定 | 執行 `write memory`，提供明顯的操作按鈕 |
| 設定備份 | 下載 `running-config` 為文字檔 |
| 設定比對 | 比較 running-config 與 startup-config 差異，以 diff 視覺化呈現 |
| 重啟設備 | 執行 `reload`，需多重確認機制 |

---

## 設定儲存與未儲存變更提醒機制

### 核心邏輯

- 網頁操作直接寫入 running-config（即時生效）
- 儲存至 startup-config 需使用者手動觸發（`write memory`）
- 系統不自動儲存，保留工程師「測試後再儲存」的操作習慣

### 變更追蹤

- 後端在 session 中維護一個「有未儲存變更」的旗標
- 每次執行寫入類指令後，將旗標設為 true
- 執行 `write memory` 後，將旗標重設為 false

### 未儲存提醒觸發時機

1. **使用者點擊登出** — 彈出 Dialog 提醒，提供三個選項：
   - 「儲存並登出」— 先執行 `write memory`，成功後斷開 SSH
   - 「不儲存直接登出」— 直接斷開 SSH
   - 「取消」— 返回操作介面
2. **關閉瀏覽器分頁/視窗** — 使用 `beforeunload` 事件攔截
3. **Session 即將超時** — 前端計時器提前跳出提醒

### 持續性視覺提示

- 頂部導航列顯示儲存狀態標籤
- 有未儲存變更時顯示醒目的「未儲存」標示
- 使用 Pinia 管理全域的儲存狀態旗標

---

## 頁面結構規劃

```
首頁（登入頁）
│
└── 主介面（登入後）
    ├── 頂部導航列
    │   ├── 設備資訊摘要（hostname, model, uptime）
    │   ├── 儲存狀態指示燈（未儲存變更提醒）
    │   ├── 儲存設定按鈕
    │   └── 登出按鈕
    │
    ├── Tab 1：Port 面板總覽
    │   ├── 視覺化 Port 面板（主區域）
    │   └── Port 詳細資訊 / 操作面板（點擊 Port 後展開）
    │       ├── 基本資訊（狀態、速率、VLAN、description）
    │       ├── IPSG 開關
    │       ├── MAC Verify 開關
    │       ├── Port Security 狀態與設定
    │       └── 介面開關（shutdown / no shutdown）
    │
    ├── Tab 2：全域安全設定
    │   ├── DHCP Snooping 狀態總覽
    │   └── 警示區塊（若前置條件未滿足）
    │
    ├── Tab 3：IP/MAC 綁定管理
    │   ├── 綁定表格（含搜尋、篩選、刪除）
    │   └── 新增綁定表單
    │
    ├── Tab 4：ARP 檢查
    │   ├── ARP Inspection 綁定資訊
    │   └── ARP Inspection 統計數據
    │
    ├── Tab 5：網路資訊
    │   ├── VLAN 管理
    │   ├── MAC Address Table
    │   ├── CDP 鄰居
    │   └── Spanning Tree 狀態
    │
    └── Tab 6：維護管理
        ├── 設定備份與下載
        ├── Running vs Startup 設定比對
        ├── 系統日誌
        └── 重啟設備
```

---

## API 設計參考

### 連線管理

```
POST   /api/connect          — 建立 SSH 連線（登入）
POST   /api/disconnect       — 斷開 SSH 連線（登出）
GET    /api/session/status   — 檢查連線狀態與未儲存變更旗標
```

### 設備資訊

```
GET    /api/device/info           — 設備基本資訊
GET    /api/device/interfaces     — 所有介面狀態（供面板使用）
GET    /api/device/interfaces/{id} — 單一介面詳細資訊
```

### Port 安全設定

```
GET    /api/security/ipsg                    — 所有 Port 的 IPSG 狀態
PUT    /api/security/ipsg/{interface}        — 設定指定 Port 的 IPSG 開關
GET    /api/security/mac-verify              — 所有 Port 的 MAC Verify 狀態
PUT    /api/security/mac-verify/{interface}  — 設定指定 Port 的 MAC Verify 開關
GET    /api/security/bindings                — IP/MAC 綁定列表
POST   /api/security/bindings                — 新增 IP/MAC 綁定
DELETE /api/security/bindings/{id}           — 刪除 IP/MAC 綁定
GET    /api/security/port-security           — Port Security 狀態
GET    /api/security/dhcp-snooping           — DHCP Snooping 全域狀態
```

### ARP 檢查

```
GET    /api/arp/bindings     — ARP Inspection 綁定資訊
GET    /api/arp/statistics   — ARP Inspection 統計
```

### 網路資訊

```
GET    /api/network/vlans            — VLAN 列表
POST   /api/network/vlans            — 新增 VLAN
DELETE /api/network/vlans/{id}       — 刪除 VLAN
GET    /api/network/mac-table        — MAC Address Table
GET    /api/network/cdp-neighbors    — CDP 鄰居
GET    /api/network/spanning-tree    — STP 狀態
```

### 維護管理

```
POST   /api/maintenance/save         — 儲存設定（write memory）
GET    /api/maintenance/config/running   — 取得 running-config
GET    /api/maintenance/config/startup   — 取得 startup-config
GET    /api/maintenance/config/diff      — running 與 startup 的差異比對
GET    /api/maintenance/logging          — 系統日誌
POST   /api/maintenance/reload           — 重啟設備
```

### 介面操作

```
PUT    /api/interfaces/{id}/shutdown     — 關閉介面
PUT    /api/interfaces/{id}/no-shutdown  — 開啟介面
PUT    /api/interfaces/{id}/config       — 修改介面設定（速率、雙工、description、VLAN）
```

---

## 專案目錄結構參考

```
project-root/
├── backend/
│   ├── main.py                    # FastAPI 入口
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth.py                # 連線管理 API
│   │   ├── device.py              # 設備資訊 API
│   │   ├── security.py            # Port 安全設定 API
│   │   ├── arp.py                 # ARP 檢查 API
│   │   ├── network.py             # 網路資訊 API
│   │   ├── interfaces.py          # 介面操作 API
│   │   └── maintenance.py         # 維護管理 API
│   ├── services/
│   │   ├── ssh_manager.py         # Netmiko SSH 連線管理
│   │   ├── command_parser.py      # CLI 輸出解析（TextFSM）
│   │   └── config_tracker.py      # 變更追蹤（未儲存旗標）
│   └── models/
│       └── schemas.py             # Pydantic 資料模型
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── stores/
│   │   │   ├── session.js         # 連線狀態、未儲存旗標
│   │   │   └── device.js          # 設備與介面資料
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   └── DashboardView.vue
│   │   ├── components/
│   │   │   ├── SwitchPanel.vue        # 視覺化 Port 面板
│   │   │   ├── PortBlock.vue          # 單一 Port 方塊元件
│   │   │   ├── PortDetailDrawer.vue   # Port 詳細資訊抽屜
│   │   │   ├── SecuritySettings.vue   # IPSG / MAC Verify 設定
│   │   │   ├── BindingTable.vue       # IP/MAC 綁定表格
│   │   │   ├── ArpInspection.vue      # ARP 檢查
│   │   │   ├── SaveStatusBadge.vue    # 儲存狀態標籤
│   │   │   └── UnsavedDialog.vue      # 未儲存提醒 Dialog
│   │   └── api/
│   │       └── index.js               # Axios API 封裝
│   └── public/
│
└── README.md
```

---

## 注意事項與限制

1. **SSH 連線管理：** 初期可採每次操作建立新連線的方式，後續再優化為連線池。
2. **前置條件檢查：** IPSG 依賴 DHCP Snooping，MAC Verify 額外依賴 Port Security，介面需在操作前自動檢查並提示。
3. **危險操作保護：** shutdown、reload、刪除 VLAN 等操作需二次確認（ElMessageBox）。
4. **表單驗證：** MAC Address 與 IP Address 的格式驗證需在前端實作。
5. **錯誤處理：** 所有 API 呼叫需處理 SSH 連線失敗、指令執行錯誤、權限不足等情境。
6. **WS-C2960X-48TS-L 限制：** 此為 L2 交換器，不支援 L3 路由功能，不需實作 ACL、QoS 等進階功能。
