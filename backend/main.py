from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_processor import processor
import config
import os

app = FastAPI(title="台北捷運壅擠度預測 API")

# 設定 CORS - 支持本地開發和線上部署
allowed_origins = [
    config.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
    "https://taipei-mrt-congestion.vercel.app",  # Vercel 前端
    "*"  # 生產環境允許所有來源
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化資料：優先使用 Git 中的預處理快取
@app.on_event("startup")
async def startup_event():
    """應用啟動時載入資料"""
    if not processor.data:
        print("\n" + "="*60)
        print("Loading Taipei MRT Congestion Data...")
        print("="*60)

        # Try to load from cache first (from Git or local)
        print("[INFO] Attempting to load from cache...")
        if processor.load_from_cache():
            print("[OK] Successfully loaded from pre-processed cache")
        else:
            print("[WARN] Cache not found, attempting to download...")
            # Fallback: download and process data if cache missing
            try:
                processor.download_and_parse_data(months=1)
                print("[OK] Data downloaded and processed")
            except Exception as e:
                print(f"[ERROR] Failed to download data: {e}")
                # Use sample data as last resort
                processor._generate_sample_data()
                print("[WARN] Using sample data as fallback")

        print("="*60 + "\n")
    else:
        print("[OK] Cache already loaded")


@app.get("/")
async def root():
    """API 健康檢查"""
    return {
        "message": "台北捷運壅擠度預測 API",
        "version": "1.0.0",
        "endpoints": {
            "GET /stations": "取得所有站點",
            "GET /congestion": "查詢特定時段壅擠程度",
            "GET /best-time": "查詢該站當天最不擠時段",
            "GET /trend": "查詢該站全天趨勢"
        }
    }


@app.get("/stations")
async def get_stations():
    """取得所有台北捷運站點"""
    stations = processor.get_stations()
    if not stations:
        raise HTTPException(status_code=500, detail="無法取得站點資料")
    return {"stations": stations}


@app.get("/congestion")
async def get_congestion(station: str, hour: int, weekday: int):
    """
    查詢特定站點、時段、星期幾的壅擠程度

    - station: 站點名稱 (e.g., "台北車站")
    - hour: 時段 0-23
    - weekday: 星期 0-6 (0=週一, 6=週日)
    """
    if not station or hour < 0 or hour > 23 or weekday < 0 or weekday > 6:
        raise HTTPException(status_code=400, detail="參數無效")

    result = processor.get_congestion(station, hour, weekday)
    if not result:
        raise HTTPException(status_code=404, detail="找不到該站點或時段資料")

    return result


@app.get("/best-time")
async def get_best_time(station: str, weekday: int, hour: int = None):
    """
    查詢該站點當天或指定時段前後最不擠的時段

    - station: 站點名稱
    - weekday: 星期 0-6
    - hour: 可選，指定的小時（0-23），將推薦該時段前後2小時內最不擠的3個時段
    """
    if not station or weekday < 0 or weekday > 6:
        raise HTTPException(status_code=400, detail="參數無效")

    if hour is not None and (hour < 0 or hour > 23):
        raise HTTPException(status_code=400, detail="小時參數無效")

    result = processor.get_best_times(station, weekday, hour=hour, top_n=3)
    if not result:
        raise HTTPException(status_code=404, detail="找不到該站點資料")

    weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    return {
        "station": station,
        "weekday": weekday,
        "weekday_name": weekdays[weekday],
        "hour": hour,
        "best_times": result
    }


@app.get("/trend")
async def get_trend(station: str, weekday: int):
    """
    查詢該站點全天 24 小時的壅擠趨勢

    - station: 站點名稱
    - weekday: 星期 0-6
    """
    if not station or weekday < 0 or weekday > 6:
        raise HTTPException(status_code=400, detail="參數無效")

    result = processor.get_daily_trend(station, weekday)
    if not result:
        raise HTTPException(status_code=404, detail="找不到該站點資料")

    return {
        "station": station,
        "weekday": weekday,
        "trend": result
    }


@app.post("/refresh-data")
async def refresh_data():
    """刷新資料（重新下載並處理）"""
    processor.download_and_parse_data()
    return {"message": "資料已刷新"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
