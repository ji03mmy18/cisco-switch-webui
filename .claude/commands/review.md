對目前的程式碼變更（或指定的檔案：**$ARGUMENTS**）進行 code review，依照此專案的規範檢查以下項目：

## 後端檢查項目

### 架構分層
- [ ] Router 層只負責接收請求與回傳結果，無業務邏輯
- [ ] 業務邏輯在 Service 層，SSH 指令透過 `ssh_manager.py` 執行
- [ ] Pydantic model 定義在 `backend/models/`
- [ ] 使用 type hints，函式與變數為 snake_case

### API 規範
- [ ] 成功回傳格式：`{ "success": true, "data": {...}, "message": "..." }`
- [ ] 錯誤回傳格式：`{ "success": false, "data": null, "message": "..." }`
- [ ] 寫入類指令執行後有更新未儲存變更旗標
- [ ] 查詢類指令（show）不影響未儲存變更旗標

### CLI 解析
- [ ] 優先使用 TextFSM template，非必要才用正則表達式

## 前端檢查項目

### 元件規範
- [ ] 使用 `<script setup>` + Composition API（無 Options API）
- [ ] API 呼叫透過 `frontend/src/api/` 層，元件內無 axios 直接呼叫
- [ ] CSS 使用 `<style scoped>`
- [ ] Element Plus 元件透過 auto-import，無手動 import

### 安全驗證
- [ ] IP 位址格式驗證（IPv4）
- [ ] MAC 位址格式驗證（`aa:bb:cc:dd:ee:ff` 或 `aabb.ccdd.eeff`）
- [ ] VLAN ID 範圍驗證（1-4094）
- [ ] 介面名稱格式驗證
- [ ] 危險操作（shutdown、reload、刪除 VLAN）有 ElMessageBox 二次確認

## 通用檢查項目

- [ ] 所有註解使用繁體中文
- [ ] 無 L3 功能（路由、ACL、NAT）
- [ ] 無自動儲存到 startup-config 的邏輯
- [ ] 無安全性漏洞（SQL injection、XSS、command injection 等）
- [ ] 無敏感資訊（密碼、金鑰）硬編碼

## 輸出格式

請列出：
1. **問題** — 不符合規範或有 bug 的地方，說明原因與建議修正方式
2. **建議** — 可改善但非強制的事項
3. **通過** — 符合規範的部分簡要說明
