# CLAUDE.md

## 專案簡介

這是一個 Cisco 交換器（WS-C2960X-48TS-L）的網頁管理介面，前後端分離架構，放在同一個 Repo 中。完整需求請參閱 `PROJECT_SPEC.md`。

## 專案結構

```
project-root/
├── backend/       # Python FastAPI 後端
├── frontend/      # Vue 3 前端
├── PROJECT_SPEC.md
└── CLAUDE.md
```

## 技術棧

### 後端

- Python 3.12
- uv (專案管理/虛擬環境)
- FastAPI
- Netmiko（SSH 通訊）
- TextFSM / NTC Templates（CLI 輸出解析）
- Pydantic（資料驗證與序列化）
- Uvicorn（ASGI Server）

### 前端

- Yarn 套件管理工具
- Vue 3（Composition API + `<script setup>` 語法）
- Vite
- Element Plus（按需引入）
- Pinia（狀態管理）
- Vue Router
- Axios（HTTP 請求）

## 程式碼風格與慣例

### 通用

- 所有程式碼中的註解使用**繁體中文**撰寫
- Commit message 遵循 Conventional Commits格式，類型使用英文，內容使用繁體中文：
  - `feat: 新增 IPSG 開關 API`
  - `fix: 修正 MAC address 驗證`
  - `refactor: 改進 SSH 連線邏輯`
- 檔案命名使用 kebab-case（例如 `ssh-manager.py`、`port-block.vue`）

### Python 後端

- 使用 type hints
- 函式與變數命名使用 snake_case
- API router 檔案放在 `backend/routers/`，每個功能領域一個檔案
- 業務邏輯放在 `backend/services/`，不要寫在 router 裡
- Pydantic model 放在 `backend/models/`
- 所有 API 回傳統一包裝格式：
  ```json
  {
    "success": true,
    "data": { ... },
    "message": "操作成功"
  }
  ```
- 錯誤回傳：
  ```json
  {
    "success": false,
    "data": null,
    "message": "SSH 連線失敗：Connection refused"
  }
  ```

### Vue 前端

- 元件使用 `<script setup>` 語法，不使用 Options API
- 元件命名使用 PascalCase（例如 `PortBlock.vue`、`SwitchPanel.vue`）
- 頁面級元件放在 `frontend/src/views/`
- 可重用元件放在 `frontend/src/components/`
- API 呼叫封裝在 `frontend/src/api/` 中，元件內不直接使用 axios
- CSS 使用 `<style scoped>`，避免全域污染
- Element Plus 元件透過 auto-import 使用，不需手動引入

## 開發指引

### 新增一個功能的標準流程

1. 在 `backend/routers/` 新增或修改對應的 API endpoint
2. 在 `backend/services/` 實作 SSH 指令發送與解析邏輯
3. 在 `frontend/src/api/` 新增對應的 API 呼叫函式
4. 在 `frontend/src/components/` 或 `views/` 建立或修改 UI 元件
5. 若涉及全域狀態（如未儲存變更旗標），更新 Pinia store

### SSH 指令相關

- 所有 Cisco CLI 指令的發送統一透過 `ssh_manager.py` 中的方法
- 寫入類指令（進入 config mode 的操作）執行後，必須更新未儲存變更旗標
- 查詢類指令（show 開頭）不影響旗標
- CLI 輸出的解析優先使用 TextFSM template，若無現成 template 再用正則表達式

### 安全與驗證

- 前端表單需驗證：
  - IP 位址格式（IPv4）
  - MAC 位址格式（支援 `aa:bb:cc:dd:ee:ff` 和 `aabb.ccdd.eeff` 格式）
  - VLAN ID 範圍（1-4094）
  - 介面名稱格式（如 `GigabitEthernet1/0/1`）
- 危險操作（shutdown、reload、刪除 VLAN）必須使用 ElMessageBox 二次確認

## 不要做的事

- 不要使用 Options API，統一使用 Composition API
- 不要在元件內直接呼叫 axios，一律透過 `api/` 層封裝
- 不要在 router 檔案裡寫業務邏輯，保持 router 層只負責接收請求和回傳結果
- 不要自動儲存設定到 startup-config，一律由使用者手動觸發
- 不要實作 L3 功能（路由、ACL、NAT），此設備為 L2 交換器
- 使用 TypeScript 進行開發

## 常用指令

```bash
# 啟動後端開發伺服器
cd backend && uv run uvicorn main:app --reload --port 8000

# 啟動前端開發伺服器
cd frontend && yarn run dev

# 安裝後端依賴
cd backend && uv sync

# 安裝前端依賴
cd frontend && yarn install
```
