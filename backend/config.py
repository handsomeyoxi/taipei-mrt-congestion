import os

# 索引 CSV URL
INDEX_CSV_URL = "https://data.taipei/api/getResourceList?scope=resourceAquire&rid=a1b4714b-3b75-4ff8-9ffc-2b411d5f0ad1"

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
