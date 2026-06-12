# 📁 專案結構詳解

## 完整目錄樹

```
taipei-mrt-congestion/
│
├── README.md                      # 完整使用說明文件
├── QUICKSTART.md                  # 快速開始指南
├── PROJECT_STRUCTURE.md           # 本檔案
├── start.bat                      # Windows 一鍵啟動腳本
├── .gitignore                     # Git 忽略規則
│
├── backend/                       # 🔧 後端資料夾
│   ├── main.py                    # FastAPI 主應用
│   │   ├─ 啟動 API 伺服器
│   │   ├─ 設置 CORS
│   │   └─ 定義所有端點
│   │
│   ├── data_processor.py          # 📊 資料處理核心
│   │   ├─ DataProcessor 類
│   │   ├─ 下載 CSV 資料
│   │   ├─ 計算壅擠程度
│   │   ├─ 管理快取
│   │   └─ 查詢和分析資料
│   │
│   ├── config.py                  # ⚙️ 配置設定
│   │   ├─ 索引 CSV URL
│   │   ├─ 壅擠程度等級定義
│   │   └─ API 設定
│   │
│   ├── requirements.txt           # 📦 Python 依賴
│   │   ├─ fastapi
│   │   ├─ uvicorn
│   │   ├─ pandas
│   │   ├─ requests
│   │   ├─ numpy
│   │   └─ pydantic
│   │
│   ├── cache/                     # 💾 資料快取目錄
│   │   ├─ congestion_data.json   # 壅擠度統計快取
│   │   ├─ stations.json          # 車站清單快取
│   │   └─ .gitkeep               # 保持目錄
│   │
│   ├── venv/                      # 🐍 虛擬環境（本地，不上傳）
│   └── .gitignore
│
├── frontend/                      # 🎨 前端資料夾
│   ├── package.json               # npm 配置和依賴
│   │   ├─ React 18
│   │   ├─ React DOM 18
│   │   ├─ Axios
│   │   └─ react-scripts
│   │
│   ├── public/                    # 🌐 靜態公開資源
│   │   └─ index.html              # HTML 入口點
│   │       └─ 定義 root 元素
│   │       └─ 基礎 SEO 設定
│   │
│   ├── src/                       # 📝 React 源代碼
│   │   ├─ index.js                # 應用入口
│   │   │  └─ 掛載 React App
│   │   │
│   │   ├─ App.js                  # 主應用程式
│   │   │  ├─ 狀態管理
│   │   │  ├─ API 調用邏輯
│   │   │  ├─ 自動查詢邏輯
│   │   │  └─ 佈局組合
│   │   │
│   │   ├─ App.css                 # 主應用樣式
│   │   │  ├─ 頁面背景
│   │   │  ├─ 佈局網格
│   │   │  └─ 動畫效果
│   │   │
│   │   └─ components/             # 🧩 React 元件
│   │       │
│   │       ├─ StationSelector.js   # 選擇器元件
│   │       │  ├─ 車站下拉選單
│   │       │  ├─ 星期幾選擇
│   │       │  ├─ 時段選擇
│   │       │  └─ onChange 事件處理
│   │       │
│   │       ├─ StationSelector.css  # 選擇器樣式
│   │       │  ├─ 網格佈局
│   │       │  ├─ 輸入框樣式
│   │       │  └─ 懸停效果
│   │       │
│   │       ├─ CongestionDisplay.js # 壅擠度顯示元件
│   │       │  ├─ 主壅擠度卡片
│   │       │  ├─ 大色塊顯示
│   │       │  ├─ 統計資訊
│   │       │  ├─ 搭車建議
│   │       │  └─ 最佳時段列表
│   │       │
│   │       ├─ CongestionDisplay.css # 顯示樣式
│   │       │  ├─ 卡片設計
│   │       │  ├─ 色塊樣式
│   │       │  ├─ 動畫過渡
│   │       │  └─ 響應式設計
│   │       │
│   │       ├─ CongestionChart.js   # 趨勢圖表元件
│   │       │  ├─ 24 小時長條圖
│   │       │  ├─ Y 軸標籤
│   │       │  ├─ 柱狀圖渲染
│   │       │  └─ 圖例說明
│   │       │
│   │       └─ CongestionChart.css  # 圖表樣式
│   │          ├─ 容器佈局
│   │          ├─ 柱狀圖設計
│   │          ├─ Y 軸樣式
│   │          └─ 圖例樣式
│   │
│   ├── .env.example               # 環境變數範本
│   ├── .gitignore                 # Node 忽略規則
│   ├── node_modules/              # npm 套件（本地，不上傳）
│   └── build/                     # 構建產出（本地，不上傳）
│
└── .git/                          # Git 版本控制（如果初始化）
```

---

## 各部分詳細說明

### 後端 (Backend)

**main.py**
- FastAPI 應用程式入口
- 定義 5 個 API 端點
- 實現 CORS 跨域支援
- 啟動時自動載入資料

**data_processor.py**
- `DataProcessor` 類：核心資料處理邏輯
- `download_and_parse_data()`: 下載 CSV 資料
- `process_dataframes()`: 計算統計數據
- `get_congestion()`: 查詢壅擠程度
- `get_best_times()`: 推薦最佳時段
- `get_daily_trend()`: 全天趨勢數據

**config.py**
- 簡化參數管理
- 定義 3 個壅擠等級
- 配置 API 和前端 URL

**cache/ 目錄**
- 快取已處理的 JSON 資料
- 加快 API 回應速度
- 避免重複計算

### 前端 (Frontend)

**App.js**
- React 應用的根元件
- 管理全局狀態
- 協調所有子元件
- 處理 API 調用

**元件層級**
```
App
├─ StationSelector (輸入控制)
├─ CongestionDisplay (結果顯示)
└─ CongestionChart (趨勢圖)
```

**CSS 模組化**
- 每個元件擁有獨立 CSS
- 避免樣式衝突
- 易於維護和修改

### 資料流

```
使用者操作
    ↓
StationSelector (選擇站點/星期/時段)
    ↓
App.js (狀態更新)
    ↓
API 調用 (axios)
    ↓
後端 (data_processor 查詢)
    ↓
返回 JSON 資料
    ↓
CongestionDisplay + CongestionChart 渲染
    ↓
視覺化展示
```

---

## 檔案名稱慣例

| 類型 | 慣例 | 範例 |
|------|------|------|
| React 元件 | PascalCase | `StationSelector.js` |
| CSS 檔案 | 跟隨 JS | `StationSelector.css` |
| Python 模組 | snake_case | `data_processor.py` |
| 配置檔案 | snake_case | `config.py` |
| 文件 | UPPERCASE.md | `README.md` |

---

## 依賴關係圖

```
前端依賴：
├─ react
├─ react-dom
├─ axios → 調用後端 API
└─ react-scripts

後端依賴：
├─ fastapi
├─ uvicorn → 運行 ASGI 伺服器
├─ pandas → 資料分析
├─ numpy → 數值計算
├─ requests → 下載 CSV
└─ pydantic → 資料驗證
```

---

## 重要檔案說明

| 檔案 | 用途 | 修改時機 |
|------|------|---------|
| `main.py` | API 端點 | 添加新功能時 |
| `data_processor.py` | 資料邏輯 | 改進計算方式時 |
| `App.js` | UI 邏輯 | 修改界面流程時 |
| `config.py` | 配置參數 | 改變設定時 |
| `.env.example` | 環境範本 | 添加新環境變數時 |
| `package.json` | 依賴版本 | 升級套件時 |
| `requirements.txt` | Python 版本 | 升級套件時 |

---

## 快速導航

想要...？去這裡：

| 需求 | 檔案 |
|------|------|
| 添加新 API 端點 | `backend/main.py` |
| 改變壅擠度計算 | `backend/data_processor.py` |
| 修改 UI 布局 | `frontend/src/App.js` |
| 改變配色 | `frontend/src/**/*.css` |
| 改變後端 URL | `frontend/src/App.js` 的 `API_BASE` |
| 啟用新資料源 | `backend/config.py` 的 `INDEX_CSV_URL` |

祝編碼愉快！🚀
