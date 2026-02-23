請依照以下規範，為目前的 git 變更撰寫並執行 commit：

## 步驟

1. 執行 `git status` 與 `git diff` 確認所有變更內容
2. 分析變更的性質與目的
3. 依照規範撰寫 commit message
4. 將相關檔案加入 staging area（優先使用具體檔案路徑，避免 `git add .`）
5. 執行 commit

## Commit Message 規範

格式：`<type>: <繁體中文描述>`

類型（type）使用英文：
- `feat` — 新增功能
- `fix` — 修正錯誤
- `refactor` — 重構（不影響功能）
- `style` — 格式調整（不影響邏輯）
- `docs` — 文件更新
- `chore` — 建構工具、依賴更新等雜項
- `test` — 測試相關

描述使用**繁體中文**，簡潔說明「做了什麼」，例如：
- `feat: 新增 IPSG 開關 API`
- `fix: 修正 MAC address 驗證邏輯`
- `refactor: 改進 SSH 連線管理模組`

## 注意事項

- 不要 commit `.env`、憑證或含有敏感資訊的檔案
- 若有多個獨立變更，評估是否應拆分為多個 commit
- Commit message 結尾加上：`Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
