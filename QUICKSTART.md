# 🚀 快速開始指南

## 最快的啟動方式（Windows）

如果你在 Windows 上，直接雙擊 `start.bat` 檔案，系統會自動：
1. ✅ 檢查 Python 和 Node.js
2. ✅ 建立虛擬環境
3. ✅ 安裝依賴
4. ✅ 啟動後端和前端伺服器

然後打開瀏覽器訪問 `http://localhost:3000` 即可！

---

## 手動啟動步驟

### Step 1: 啟動後端 (終端 1)

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動伺服器
python main.py
```

✅ 看到 `Application startup complete` 代表成功

在 `http://localhost:8000/docs` 可以看到 API 文件

### Step 2: 啟動前端 (終端 2)

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm start
```

✅ 瀏覽器會自動打開 `http://localhost:3000`

---

## 第一次使用

1. **選擇車站** - 從下拉選單選擇台北捷運任一車站
2. **選擇星期幾** - 選擇你要查詢的日期
3. **選擇時段** - 選擇你要查詢的小時
4. **查看結果** - 自動顯示：
   - 🟢 壅擠程度（綠/黃/紅）
   - 📊 全天趨勢圖
   - ✨ 推薦搭車時段

---

## 測試資料

首次啟動時，系統會使用**示例資料**讓你快速體驗功能。

要使用**真實台北捷運資料**，在後端啟動後執行：

```bash
curl -X POST http://localhost:8000/refresh-data
```

系統會自動下載最新的 CSV 資料並處理。

---

## 常見問題

**Q: 後端啟動失敗？**
A: 確保已安裝 Python 3.8+ 和所有依賴。查看錯誤信息並重新執行 `pip install -r requirements.txt`

**Q: 前端顯示空白？**
A: 
- 檢查後端是否正在運行
- 打開瀏覽器開發工具（F12）查看 Console
- 確認沒有 CORS 錯誤

**Q: 資料沒有更新？**
A: 執行 `POST /refresh-data` 刷新資料，或重啟後端伺服器

**Q: 能在手機上使用嗎？**
A: 可以。將 `frontend/src/App.js` 中的 `localhost` 改為你電腦的 IP 位址（例如 `192.168.1.100`）

---

## 下一步

詳細說明請參考 [README.md](./README.md)

- 📚 完整 API 文件：`http://localhost:8000/docs`
- 🎨 自訂樣式：編輯 `frontend/src/components/*.css`
- 🔧 調整資料處理：編輯 `backend/data_processor.py`

祝你使用愉快！🎉
