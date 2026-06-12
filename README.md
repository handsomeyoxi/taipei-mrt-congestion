# 🚇 台北捷運壅擠度預測

一個幫助台北市民找到最舒適搭車時間的網站。透過分析台北捷運每日分時各站 OD 流量統計資料，預測各站各時段的壅擠程度。

## 功能特性

✨ **壅擠度預測**
- 查詢指定車站、時段、星期幾的壅擠程度
- 三個等級視覺化：低（綠）/ 中（黃）/ 高（紅）

✨ **智能搭車建議**
- 推薦當天最不擁擠的 3 個時段
- 基於真實數據的個人化建議

✨ **全天趨勢分析**
- 24 小時長條圖展示該站全天壅擠趨勢
- 快速識別高峰期和低谷期

✨ **友善使用者介面**
- 直觀的下拉選單選擇車站、星期幾、時段
- 實時更新，無需點擊查詢按鈕
- 響應式設計，支援手機和平板

## 技術堆疊

**後端**
- Python FastAPI - 高效能 Web 框架
- Pandas - 資料處理和分析
- Requests - 下載 CSV 資料
- CORS 支援

**前端**
- React 18 - 用戶介面框架
- Axios - API 請求
- CSS3 - 現代化樣式

**資料來源**
- 台北捷運每日分時各站 OD 流量統計 CSV
- 自動下載並解析最新資料

## 專案結構

```
taipei-mrt-congestion/
├── backend/                    # 後端
│   ├── main.py                # FastAPI 主應用
│   ├── data_processor.py       # 資料處理邏輯
│   ├── config.py              # 配置設定
│   ├── cache/                 # 資料快取目錄
│   │   ├── congestion_data.json
│   │   └── stations.json
│   └── requirements.txt        # Python 依賴
│
├── frontend/                   # 前端
│   ├── src/
│   │   ├── App.js             # 主應用程式
│   │   ├── App.css
│   │   ├── index.js           # 入口點
│   │   └── components/
│   │       ├── StationSelector.js   # 車站選擇器
│   │       ├── CongestionDisplay.js # 壅擠度顯示
│   │       ├── CongestionChart.js   # 趨勢圖表
│   │       └── *.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── .gitignore
│
└── README.md                   # 本檔案
```

## 安裝和執行

### 前置要求

- Python 3.8+
- Node.js 14+ 和 npm
- Git（可選）

### 後端設置

1. **進入後端目錄**
   ```bash
   cd backend
   ```

2. **建立虛擬環境**（推薦）
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS / Linux
   source venv/bin/activate
   ```

3. **安裝 Python 依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **啟動後端伺服器**
   ```bash
   python main.py
   ```
   
   或使用 uvicorn:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

   ✅ 後端會在 `http://localhost:8000` 啟動
   
   API 文件：`http://localhost:8000/docs` (Swagger UI)

### 前端設置

1. **開啟新的終端，進入前端目錄**
   ```bash
   cd frontend
   ```

2. **安裝 npm 依賴**
   ```bash
   npm install
   ```

3. **啟動開發伺服器**
   ```bash
   npm start
   ```
   
   ✅ 前端會自動開啟 `http://localhost:3000`

## 使用方式

1. 從下拉選單選擇要查詢的**車站**
2. 選擇要查詢的**星期幾**
3. 選擇要查詢的**時段**（0-23 點）
4. 結果會自動更新，顯示：
   - 該時段的壅擠程度（大色塊）
   - 平均進站人次
   - 搭車建議
   - 當天最不擁擠的 3 個時段
   - 全天 24 小時壅擠趨勢圖

## API 端點

### 取得所有車站
```
GET /stations
```

回應:
```json
{
  "stations": ["台北車站", "中山", "台北101/世貿", ...]
}
```

### 查詢壅擠程度
```
GET /congestion?station=台北車站&hour=8&weekday=1
```

參數:
- `station` (string): 車站名稱
- `hour` (int): 時段 0-23
- `weekday` (int): 星期 0-6 (0=週一, 6=週日)

回應:
```json
{
  "station": "台北車站",
  "hour": 8,
  "weekday": 1,
  "people": 2850.5,
  "level": "high",
  "color": "red",
  "label": "高",
  "suggestion": "現在搭車很擁擠，建議改時段"
}
```

### 取得最佳搭車時段
```
GET /best-time?station=台北車站&weekday=1
```

參數:
- `station` (string): 車站名稱
- `weekday` (int): 星期 0-6

回應:
```json
{
  "station": "台北車站",
  "weekday": 1,
  "weekday_name": "週二",
  "best_times": [
    {
      "hour": 2,
      "people": 120.0,
      "level": "low",
      "label": "低"
    },
    ...
  ]
}
```

### 取得全天趨勢
```
GET /trend?station=台北車站&weekday=1
```

參數:
- `station` (string): 車站名稱
- `weekday` (int): 星期 0-6

回應:
```json
{
  "station": "台北車站",
  "weekday": 1,
  "trend": [
    {
      "hour": 0,
      "people": 120.0,
      "level": "low",
      "color": "green"
    },
    ...
  ]
}
```

### 刷新資料
```
POST /refresh-data
```

重新下載並處理最新的 CSV 資料。

## 資料快取

後端自動將處理後的資料快取到 JSON 檔案，以提升性能：

- `backend/cache/congestion_data.json` - 各站各時段壅擁度統計
- `backend/cache/stations.json` - 車站清單

首次啟動時會自動生成示例資料。使用真實台北捷運資料時，調用 `POST /refresh-data` 端點重新下載。

## 壅擁度計算方式

根據該時段的進站人次分位數計算：

- **低壅擠（綠）**: 0-33% 百分位數
- **中壅擠（黃）**: 33-66% 百分位數  
- **高壅擠（紅）**: 66-100% 百分位數

## 常見問題

### Q: 為什麼顯示示例資料？
A: 首次啟動時，系統會自動生成示例資料供演示。要使用真實資料，需要執行 `POST /refresh-data` 端點，系統會自動下載台北捷運的 CSV 檔案。

### Q: 資料多久更新一次？
A: 資料快取在記憶體中，重啟後端伺服器時會重新載入。要手動更新，調用 `POST /refresh-data` 端點。

### Q: 前端和後端在不同機器上可以嗎？
A: 可以。修改 `frontend/src/App.js` 中的 `API_BASE` 和 `backend/config.py` 中的 `FRONTEND_URL` 即可。

### Q: 如何在生產環境部署？
A: 
- 後端：使用 Gunicorn 或其他 ASGI 伺服器
- 前端：執行 `npm build` 生成靜態檔案，配置 Web 伺服器（Nginx、Apache 等）

## 故障排除

### 連線問題
- 確認後端伺服器運行在 `http://localhost:8000`
- 檢查防火牆是否允許連接
- 查看瀏覽器開發工具的 Network 標籤

### 資料載入失敗
- 檢查網路連線
- 查看後端控制台日誌
- 嘗試重啟後端伺服器

### CORS 錯誤
- 確認後端已啟用 CORS
- 檢查 `config.py` 中的 `FRONTEND_URL` 設定

## 效能優化建議

1. **資料快取** - 已實現，減少重複計算
2. **API 快取頭** - 在生產環境中添加適當的 Cache-Control
3. **資料分頁** - 若站點數過多，考慮分頁查詢
4. **前端優化** - 使用 React.memo 和 useMemo 優化重繪

## 隱私和資料保護

本應用僅使用公開的台北捷運 OD 流量統計資料，不蒐集個人資訊。所有資料處理均在本地進行。

## 授權

本專案用於教育和學習目的。

## 開發者

為軟體工程課程期末作業和鐵道數據創新競賽開發。

## 致謝

- 台北捷運公司提供的資料
- FastAPI 和 React 社群

---

**開始使用**: 按照上述步驟安裝和執行，然後打開 `http://localhost:3000` 享受舒適的捷運體驗！ 🚇✨
