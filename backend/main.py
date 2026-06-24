from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_processor import processor
import config
import os

app = FastAPI(title="台北捷運擁擠度預測 API")

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
            print("[WARN] Cache not found, using lightweight lazy loading...")
            # For memory-constrained environments (e.g., Render free tier),
            # initialize with lazy loading instead of pre-loading everything
            processor._generate_sample_data()
            print("[WARN] Initialized with lazy loading - data generated on-demand")

        print("="*60 + "\n")
    else:
        print("[OK] Cache already loaded")


@app.get("/")
async def root():
    """API 健康檢查"""
    return {
        "message": "台北捷運擁擠度預測 API",
        "version": "1.0.0",
        "endpoints": {
            "GET /stations": "取得所有站點",
            "GET /congestion": "查詢特定時段擁擠程度",
            "GET /best-time": "查詢該站當天最不擠時段",
            "GET /trend": "查詢該站全天趨勢"
        }
    }


@app.get("/stations")
async def get_stations():
    """取得所有台北捷運站點（純站名和線路映射）"""
    print(f"\n[DEBUG] /stations endpoint called")

    stations, station_lines = processor.get_stations_with_lines()
    print(f"[DEBUG] 取得 {len(stations)} 個純站名")
    print(f"[DEBUG] 前10個: {stations[:10]}")
    print(f"[DEBUG] 線路映射範例: 板橋 -> {station_lines.get('板橋')}, 南勢角 -> {station_lines.get('南勢角')}")

    if not stations:
        raise HTTPException(status_code=500, detail="無法取得站點資料")

    return {
        "stations": stations,
        "station_lines": station_lines
    }


@app.get("/congestion")
async def get_congestion(line: str, station: str, hour: int, weekday: int):
    """
    查詢特定站點、時段、星期幾的擁擠程度

    - line: 線路代碼 (e.g., "R", "BL", "BR") - 必須
    - station: 純站名 (e.g., "台北車站") - 必須
    - hour: 時段 0-23
    - weekday: 星期 0-6 (0=週一, 6=週日)
    """
    print(f"\n[DEBUG] /congestion endpoint called")
    print(f"[DEBUG] 收到的參數: line='{line}' (type: {type(line).__name__}), station='{station}' (type: {type(station).__name__})")
    print(f"[DEBUG] 收到的 hour: {hour}, weekday: {weekday}")

    if not line or not station or hour < 0 or hour > 23 or weekday < 0 or weekday > 6:
        print(f"[DEBUG] ✗ 參數驗證失敗: line={repr(line)}, station={repr(station)}")
        raise HTTPException(status_code=400, detail="參數無效")

    print(f"[DEBUG] ✓ 參數驗證通過")

    # 查詢（先試純站名，再試帶前綴）
    result = processor.get_congestion(station, hour, weekday, line=line)
    if not result:
        print(f"[DEBUG] ✗ processor.get_congestion() 返回 None")
        raise HTTPException(status_code=404, detail="找不到該站點或時段資料")

    print(f"[DEBUG] ✓ /congestion 成功: station={result['station']}, level={result['level']}, people={result['people']}")
    return result


@app.get("/best-time")
async def get_best_time(line: str, station: str, weekday: int, hour: int = None, time_range: int = 2):
    """
    查詢該站點當天或指定時段前後最不擠的時段

    - line: 線路代碼 (e.g., "R", "BL", "BR") - 必須
    - station: 純站名 (e.g., "台北車站") - 必須
    - weekday: 星期 0-6
    - hour: 可選，指定的小時（0-23），將推薦該時段前後N小時內最不擠的3個時段
    - time_range: 時間範圍（小時），預設 2（±2小時），可選 1 或 3
    """
    print(f"\n[DEBUG] /best-time endpoint called")
    print(f"[DEBUG] 收到的參數: line='{line}' (type: {type(line).__name__}), station='{station}' (type: {type(station).__name__})")

    if not line or not station or weekday < 0 or weekday > 6:
        print(f"[DEBUG] ✗ 參數驗證失敗: line={repr(line)}, station={repr(station)}, weekday={weekday}")
        raise HTTPException(status_code=400, detail="參數無效")

    print(f"[DEBUG] ✓ 參數驗證通過")

    if hour is not None and (hour < 0 or hour > 23):
        raise HTTPException(status_code=400, detail="小時參數無效")

    if time_range not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="時間範圍必須是 1、2 或 3")

    # 查詢（先試純站名，再試帶前綴）
    result = processor.get_best_times(station, weekday, hour=hour, time_range=time_range, top_n=3, line=line)
    if not result:
        print(f"[DEBUG] ✗ processor.get_best_times() 返回空結果")
        raise HTTPException(status_code=404, detail="找不到該站點資料")

    print(f"[DEBUG] ✓ /best-time 成功: 找到 {len(result)} 個推薦時段")
    weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    return {
        "station": station,
        "weekday": weekday,
        "weekday_name": weekdays[weekday],
        "hour": hour,
        "best_times": result
    }


@app.get("/trend")
async def get_trend(line: str, station: str, weekday: int):
    """
    查詢該站點全天 24 小時的擁擠趨勢

    - line: 線路代碼 (e.g., "R", "BL", "BR") - 必須
    - station: 純站名 (e.g., "台北車站") - 必須
    - weekday: 星期 0-6
    """
    print(f"\n[DEBUG] /trend endpoint called")
    print(f"[DEBUG] 收到的參數: line='{line}' (type: {type(line).__name__}), station='{station}' (type: {type(station).__name__})")

    if not line or not station or weekday < 0 or weekday > 6:
        print(f"[DEBUG] ✗ 參數驗證失敗: line={repr(line)}, station={repr(station)}, weekday={weekday}")
        raise HTTPException(status_code=400, detail="參數無效")

    print(f"[DEBUG] ✓ 參數驗證通過")

    # 查詢（先試純站名，再試帶前綴）
    result = processor.get_daily_trend(station, weekday, line=line)
    if not result:
        print(f"[DEBUG] ✗ processor.get_daily_trend() 返回空結果")
        raise HTTPException(status_code=404, detail="找不到該站點資料")

    print(f"[DEBUG] ✓ /trend 成功: 找到 {len(result)} 個小時的趨勢資料")
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
