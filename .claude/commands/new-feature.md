依照此專案的標準開發流程，協助實作新功能：**$ARGUMENTS**

## 標準開發流程

請依序完成以下步驟，每步驟完成後確認再繼續：

### 步驟 1：需求分析
- 閱讀 `PROJECT_SPEC.md` 確認功能需求範圍
- 確認此功能屬於哪個功能領域（登入、Port 管理、VLAN、安全功能等）
- 確認涉及的 Cisco CLI 指令（查詢類 / 寫入類）

### 步驟 2：後端 Router
- 在 `backend/routers/` 新增或修改對應的 router 檔案
- Router 只負責接收請求與回傳結果，不寫業務邏輯
- 所有回傳使用統一格式：
  ```json
  { "success": true, "data": { ... }, "message": "操作成功" }
  ```

### 步驟 3：後端 Service
- 在 `backend/services/` 實作 SSH 指令發送與解析邏輯
- 透過 `ssh_manager.py` 發送 CLI 指令
- 解析優先使用 TextFSM template，其次才用正則表達式
- 寫入類指令執行後，必須更新未儲存變更旗標

### 步驟 4：後端 Model（若需要）
- 在 `backend/models/` 定義 Pydantic model
- 使用 type hints，snake_case 命名

### 步驟 5：前端 API 層
- 在 `frontend/src/api/` 新增對應的 API 呼叫函式
- 元件內不直接使用 axios

### 步驟 6：前端 UI 元件
- 頁面級元件放 `frontend/src/views/`，可重用元件放 `frontend/src/components/`
- 使用 `<script setup>` + Composition API，不使用 Options API
- Element Plus 元件透過 auto-import 使用
- CSS 使用 `<style scoped>`
- 危險操作加上 ElMessageBox 二次確認

### 步驟 7：狀態管理（若需要）
- 若涉及全域狀態（如未儲存變更旗標），更新 Pinia store

## 注意事項
- 此設備為 L2 交換器，不實作 L3 功能（路由、ACL、NAT）
- 不要自動儲存設定到 startup-config
- 所有註解使用繁體中文
