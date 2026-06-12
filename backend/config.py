import os

# 索引 CSV URL - 從台北市開放資料平台取得最近3個月的 MRT OD 流量資料
# 資料集: 台北捷運每日分時各站OD流量統計資料
INDEX_CSV_URL = "https://data.taipei/api/v1/dataset/63f31c7e-7fc3-418b-bd82-b95158755b4d?limit=100"

# 資料快取目錄
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

# 壅擁程度等級定義（基於進站人次百分位）
# 低：0-33%  (綠)
# 中：33-66% (黃)
# 高：66-100% (紅)
CONGESTION_LEVELS = {
    "low": {"color": "green", "label": "低", "range": (0, 0.33)},
    "medium": {"color": "yellow", "label": "中", "range": (0.33, 0.66)},
    "high": {"color": "red", "label": "高", "range": (0.66, 1.0)},
    "closed": {"color": "gray", "label": "未營運", "range": (0, 0)}
}

# API 相關設定
API_HOST = "127.0.0.1"
API_PORT = 8000
FRONTEND_URL = "http://localhost:3000"
