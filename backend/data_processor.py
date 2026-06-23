import os
import json
import requests
import pandas as pd
import numpy as np
from config import CACHE_DIR, CONGESTION_LEVELS
from datetime import datetime

# Suppress SSL warnings when verify=False is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.makedirs(CACHE_DIR, exist_ok=True)

# Cache version to force refresh when logic changes
CACHE_VERSION = 13  # Increment to invalidate old caches

# MRT Line Mapping - 硬編碼每條線的所有站點
STATION_LINE_MAPPING = {}

# 文湖線（棕線）BR - 24個站點
BR_STATIONS = ['動物園', '木柵', '萬芳社區', '萬芳醫院', '辛亥', '麟光', '六張犁', '科技大樓',
               '大安', '忠孝復興', '南京復興', '中山國中', '松山機場', '大直', '劍南路', '西湖',
               '港墘', '文德', '內湖', '大湖公園', '葫洲', '東湖', '南港軟體園區', '南港展覽館']

# 淡水信義線（紅線）R - 28個站點
R_STATIONS = ['淡水', '紅樹林', '竹圍', '關渡', '忠義', '復興崗', '北投', '新北投', '奇岩',
              '唭哩岸', '石牌', '明德', '芝山', '士林', '劍潭', '圓山', '民權西路', '雙連',
              '中山', '台北車站', '台大醫院', '中正紀念堂', '東門', '大安森林公園', '大安',
              '信義安和', '台北101/世貿', '象山']

# 松山新店線（綠線）G - 19個站點
G_STATIONS = ['松山', '南京三民', '台北小巨蛋', '南京復興', '忠孝新生', '善導寺', '台北車站',
              '小南門', '中正紀念堂', '古亭', '台電大樓', '公館', '萬隆', '景美', '大坪林',
              '七張', '新店區公所', '新店', '小碧潭']

# 中和新蘆線（橘線）O - 24個站點
O_STATIONS = ['迴龍', '丹鳳', '輔大', '新莊', '頭前庄', '先嗇宮', '三重國小', '三和國中',
              '蘆洲', '大橋頭', '台北橋', '菜寮', '三重', '新埔民生', '中山國小', '行天宮',
              '松江南京', '忠孝新生', '東門', '古亭', '頂溪', '永安市場', '景安', '南勢角']

# 板南線（藍線）BL - 23個站點
BL_STATIONS = ['頂埔', '永寧', '土城', '海山', '亞東醫院', '府中', '板橋', '新埔', '江子翠',
               '龍山寺', '西門', '台北車站', '善導寺', '忠孝新生', '忠孝復興', '忠孝敦化', '國父紀念館',
               '市政府', '永春', '後山埤', '昆陽', '南港', '南港展覽館']

# 環狀線（黃線）Y - 21個站點
Y_STATIONS = ['新北產業園區', '幸福', '頭前庄', '新莊', '丹鳳', '輔大', '新埔', '迴龍', '中原',
              '板橋', '板新', '大坪林', '十四張', '秀朗橋', '景平', '景安', '中和', '橋和',
              '永安市場', '南勢角', '頂溪']

# 建立映射 - 每個站可以屬於多條線（轉乘站）
for station in BR_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('BR')
for station in R_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('R')
for station in G_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('G')
for station in O_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('O')
for station in BL_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('BL')
for station in Y_STATIONS:
    if station not in STATION_LINE_MAPPING:
        STATION_LINE_MAPPING[station] = []
    STATION_LINE_MAPPING[station].append('Y')

class DataProcessor:
    def __init__(self):
        self.cache_file = os.path.join(CACHE_DIR, "congestion_data.json")
        self.stations_file = os.path.join(CACHE_DIR, "stations.json")
        self.version_file = os.path.join(CACHE_DIR, "version.txt")
        self.data = {}
        self.station_percentiles = {}  # Store P33/P66 for each station
        self.load_from_cache()

    def get_station_with_line_code(self, station_name):
        """Get station name with line code prefix based on hardcoded mapping"""
        if station_name in STATION_LINE_MAPPING:
            line_codes = STATION_LINE_MAPPING[station_name]
            # Use first line code for prefix (for transfer stations)
            line_code = line_codes[0] if isinstance(line_codes, list) else line_codes
            return f"{line_code}{station_name}"
        # If station not in mapping, return as is (shouldn't happen)
        return station_name

    def get_station_lines(self, station_name):
        """Get all line codes for a station (handles transfer stations)"""
        if station_name in STATION_LINE_MAPPING:
            line_codes = STATION_LINE_MAPPING[station_name]
            return line_codes if isinstance(line_codes, list) else [line_codes]
        return []

    def load_from_cache(self):
        """From cache load data"""
        # Check version first
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    cached_version = int(f.read().strip())
                if cached_version != CACHE_VERSION:
                    print(f"[INFO] Cache version mismatch (cached: {cached_version}, current: {CACHE_VERSION}) - invalidating cache")
                    return False
            except:
                pass

        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"[OK] Cache loaded: {len(self.data)} stations")
                return True
            except Exception as e:
                print(f"[WARN] Cache read failed: {e}")
        return False

    def save_to_cache(self):
        """Save data to cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            # Save version file
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(str(CACHE_VERSION))
            print(f"[OK] Data cached: {self.cache_file} (version {CACHE_VERSION})")
        except Exception as e:
            print(f"[ERROR] Cache save failed: {e}")

    def get_fixed_data_urls(self):
        """Get fixed data URL from Azure Blob Storage (latest month only for low memory)"""
        # Only latest month to fit in Render free tier (512MB RAM)
        urls = [
            "http://tcgmetro.blob.core.windows.net/stationod/臺北捷運每日分時各站OD流量統計資料_202501.csv",
        ]
        print(f"[OK] Using fixed data URLs ({len(urls)} month) - optimized for low memory:")
        for url in urls:
            print(f"     {url}")
        return urls

    def fetch_index_csv_local(self, csv_path, months=3):
        """Get latest N months data URLs from local CSV"""
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')

            # Sort by year and month, get latest N months
            df = df.sort_values(['西元年', '月'], ascending=False)
            latest_n = df.head(months).sort_values(['西元年', '月'])

            urls = latest_n['URL'].tolist()
            dates = latest_n.apply(lambda x: f"{int(x['西元年'])}-{int(x['月']):02d}", axis=1).tolist()

            print(f"[OK] Got {len(urls)} data URLs from index: {dates}")
            return urls
        except Exception as e:
            print(f"[ERROR] Index CSV read failed: {e}")
            return []

    def fetch_index_csv(self):
        """Get data URLs from Taipei Open Data API"""
        try:
            from config import INDEX_CSV_URL
            print(f"[INFO] Fetching from: {INDEX_CSV_URL}")
            # Skip SSL verification for data.taipei API
            response = requests.get(INDEX_CSV_URL, timeout=30, verify=False)
            response.encoding = 'utf-8'

            # Parse JSON response - handle multiple API formats
            data = response.json()

            # Debug: Print full response structure
            print(f"\n[DEBUG] ===== Full API Response =====")
            print(f"Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"Top-level keys: {list(data.keys())}")
                # Print full response with indentation
                import json as json_lib
                print(json_lib.dumps(data, ensure_ascii=False, indent=2)[:2000])  # First 2000 chars
            else:
                print(f"Response: {str(data)[:500]}")
            print(f"[DEBUG] ===== End API Response =====\n")

            urls = []

            # Format 1: {result: {results: [...]}}
            if isinstance(data, dict) and 'result' in data and 'results' in data.get('result', {}):
                print(f"[DEBUG] Detected Format 1: result.results")
                for item in data['result']['results']:
                    # Look for download URL in different field names
                    url = item.get('downloadURL') or item.get('resourceURL') or item.get('url')
                    if url:
                        urls.append(url)

            # Format 2: Direct array of resources
            elif isinstance(data, list):
                print(f"[DEBUG] Detected Format 2: Direct array")
                for item in data:
                    url = item.get('downloadURL') or item.get('resourceURL') or item.get('url')
                    if url:
                        urls.append(url)

            # Format 3: {results: [...]} (without result wrapper)
            elif isinstance(data, dict) and 'results' in data:
                print(f"[DEBUG] Detected Format 3: results (no wrapper)")
                for item in data['results']:
                    url = item.get('downloadURL') or item.get('resourceURL') or item.get('url')
                    if url:
                        urls.append(url)

            # Format 4: Try to find result.results structure even if it's nested differently
            elif isinstance(data, dict) and 'result' in data:
                result = data['result']
                print(f"[DEBUG] Found 'result' key, investigating structure...")
                print(f"[DEBUG] result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"[DEBUG] result keys: {list(result.keys())}")
                    # Try to find results or resources
                    if 'results' in result:
                        print(f"[DEBUG] Found result.results, extracting...")
                        for item in result.get('results', []):
                            print(f"[DEBUG] Item keys: {list(item.keys()) if isinstance(item, dict) else type(item)}")
                            # Check all possible field names
                            for field in ['downloadURL', 'resourceURL', 'url', 'download_url', 'resource_url',
                                        'URL', 'downloadUrl', 'resourceUrl', 'href', 'uri', 'link']:
                                if field in item:
                                    urls.append(item[field])
                                    print(f"[DEBUG] Found URL in field '{field}': {item[field][:50]}...")
                                    break
                    elif isinstance(result, list):
                        print(f"[DEBUG] result is a list with {len(result)} items")
                        for item in result:
                            print(f"[DEBUG] Item: {str(item)[:200]}")

            if urls:
                print(f"[OK] Got {len(urls)} data URLs from API")
                for i, url in enumerate(urls[:3], 1):  # Show first 3 URLs
                    print(f"     URL {i}: {url[:80]}...")
            else:
                print(f"[WARN] No download URLs found in API response")
                if isinstance(data, dict):
                    print(f"[DEBUG] Response keys: {list(data.keys())}")
                    if 'result' in data:
                        result = data['result']
                        if isinstance(result, dict):
                            print(f"[DEBUG] result keys: {list(result.keys())}")

            return urls
        except Exception as e:
            print(f"[ERROR] Index CSV fetch failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def download_and_parse_data(self, urls=None, csv_path=None, months=1):
        """Download and parse monthly data"""
        # Use local index CSV if provided
        if csv_path and os.path.exists(csv_path):
            print(f"[INFO] Reading local index CSV: {csv_path}")
            urls = self.fetch_index_csv_local(csv_path, months=months)

        # If no URLs yet, use fixed URLs from Azure Blob Storage
        if urls is None or len(urls) == 0:
            print(f"[INFO] Using fixed data URLs from Azure Blob Storage...")
            urls = self.get_fixed_data_urls()

        # If still no URLs, use sample data as fallback
        if urls is None or len(urls) == 0:
            print("[WARN] Unable to get data URLs, using sample data")
            self._generate_sample_data()
            return

        all_data = []
        for i, url in enumerate(urls, 1):
            try:
                print(f"[{i}/{len(urls)}] Streaming: {url[-30:]}")
                # Stream the CSV data to minimize memory usage
                # Skip SSL verification
                response = requests.get(url, timeout=60, verify=False, stream=True)
                response.encoding = 'utf-8'

                # Read CSV in chunks to avoid loading entire file in memory
                import io
                chunks = []
                chunk_count = 0
                chunk_size = 50000  # Process 50k rows at a time

                for chunk in pd.read_csv(io.BytesIO(response.content),
                                         chunksize=chunk_size,
                                         dtype={'人次': 'int32', '日期': 'str', '時段': 'int16'}):
                    chunks.append(chunk)
                    chunk_count += 1
                    if chunk_count % 10 == 0:
                        print(f"     Processing chunk {chunk_count}...")

                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                    all_data.append(df)
                    print(f"     [OK] Streamed {len(df):,} records in {chunk_count} chunks")

            except Exception as e:
                print(f"     [ERROR] Download failed: {str(e)[:80]}")
                import traceback
                traceback.print_exc()

        if all_data:
            print(f"[INFO] Concatenating {len(all_data)} files...")
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"[OK] Total data: {len(combined_df):,} records")
            print(f"\n=== Data Diagnostics ===")
            print(f"Columns: {list(combined_df.columns)}")
            print(f"Date range: {combined_df['日期'].min()} to {combined_df['日期'].max()}")
            print(f"Sample rows:")
            print(combined_df[['日期', '時段', '進站', '出站', '人次']].head(10).to_string())
            print(f"\nBasic stats - 人次:")
            print(f"  Max: {combined_df['人次'].max()}")
            print(f"  Mean: {combined_df['人次'].mean():.2f}")
            print(f"  Median: {combined_df['人次'].median():.2f}")
            print(f"========================\n")
            self.process_dataframes(combined_df)
        else:
            print("[WARN] All downloads failed, using sample data")
            self._generate_sample_data()

    def process_dataframes(self, df):
        """Process DataFrame and calculate statistics - optimized for low memory"""
        # Ensure column names are clean and handle BOM
        df.columns = df.columns.str.strip()
        df.columns = [col.replace('﻿', '') for col in df.columns]  # Remove BOM

        print(f"\n=== Processing Data ===")
        print(f"Columns: {list(df.columns)}")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Parse date - handle both formats (YYYYMMDD and YYYY-MM-DD)
        try:
            df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
        except:
            try:
                df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
            except:
                df['日期'] = pd.to_datetime(df['日期'], format='mixed')

        # Convert to int16 to save memory (weekday only needs 0-6)
        df['weekday'] = df['日期'].dt.weekday.astype('int8')
        df['時段'] = df['時段'].astype('int8')

        # Keep only needed columns to save memory
        df = df[['進站', '時段', 'weekday', '日期', '人次']]

        print(f"After optimization: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")

        # Group by [station, hour, weekday]
        # First: sum all destinations for each station/hour/weekday/date
        print("[INFO] Grouping by station/hour/weekday/date...")
        daily = df.groupby(['進站', '時段', 'weekday', '日期'])['人次'].sum().reset_index()
        daily.columns = ['station', 'hour', 'weekday', 'date', 'daily_total']

        # Delete original df to free memory
        del df
        import gc
        gc.collect()

        # Second: average across all dates
        print("[INFO] Calculating daily averages...")
        grouped = daily.groupby(['station', 'hour', 'weekday'])['daily_total'].mean().reset_index()
        grouped.columns = ['station', 'hour', 'weekday', 'avg_people']

        # Delete daily to free memory
        del daily
        gc.collect()

        # MRT operating hours: 06:00-23:59 (hours 6-23)
        MRT_OPERATING_HOURS = set(range(6, 24))

        # Organize by station
        self.data = {}
        self.station_percentiles = {}

        for station in grouped['station'].unique():
            station_data = grouped[grouped['station'] == station]

            # Calculate percentiles FOR THIS STATION ONLY
            station_operating = station_data[station_data['hour'].isin(MRT_OPERATING_HOURS)]
            station_people = station_operating['avg_people'].values
            p33 = np.percentile(station_people, 33)
            p66 = np.percentile(station_people, 66)

            # Add line code prefix to station name
            station_with_code = self.get_station_with_line_code(station)

            # Store the percentiles for this station (with line code prefix)
            self.station_percentiles[station_with_code] = {
                "p33": round(p33, 1),
                "p66": round(p66, 1),
                "min": round(station_people.min(), 1),
                "max": round(station_people.max(), 1)
            }

            station_dict = {}

            for weekday in range(7):
                weekday_data = station_data[station_data['weekday'] == weekday]
                hours = {}

                for _, row in weekday_data.iterrows():
                    hour = int(row['hour'])
                    people = row['avg_people']

                    # Check if operating
                    if hour not in MRT_OPERATING_HOURS:
                        # Not operating
                        hours[str(hour)] = {
                            "people": 0,
                            "level": "closed",
                            "is_operating": False
                        }
                    else:
                        # Operating - determine level using THIS STATION'S percentiles
                        if people <= p33:
                            level = "low"
                        elif people <= p66:
                            level = "medium"
                        else:
                            level = "high"

                        hours[str(hour)] = {
                            "people": round(people, 1),
                            "level": level,
                            "is_operating": True
                        }

                # Fill missing operating hours
                station_operating = station_data[station_data['hour'].isin(MRT_OPERATING_HOURS)]
                if len(station_operating) > 0:
                    station_avg = station_operating['avg_people'].mean()
                    for h in range(6, 24):
                        if str(h) not in hours:
                            if station_avg <= p33:
                                level = "low"
                            elif station_avg <= p66:
                                level = "medium"
                            else:
                                level = "high"
                            hours[str(h)] = {
                                "people": round(station_avg, 1),
                                "level": level,
                                "is_operating": True
                            }

                # Fill non-operating hours (0-5)
                for h in range(0, 6):
                    if str(h) not in hours:
                        hours[str(h)] = {
                            "people": 0,
                            "level": "closed",
                            "is_operating": False
                        }

                station_dict[str(weekday)] = hours

            # Store data with line code prefix
            self.data[station_with_code] = station_dict

        print(f"[OK] Processed {len(self.data)} stations")

        # Print diagnostics - show percentiles for all stations
        print(f"\n=== Percentile Thresholds by Station ===")
        print(f"{'Station':<15} | {'P33 (Low/Mid)':<15} | {'P66 (Mid/High)':<15}")
        print("-" * 50)
        for station in sorted(self.station_percentiles.keys()):
            p = self.station_percentiles[station]
            print(f"{station:<15} | {p['p33']:<15.1f} | {p['p66']:<15.1f}")
        print("=" * 50)

        # Show sample station details
        print(f"\n=== Sample Station Details ===")
        sample_station = list(self.data.keys())[0]
        print(f"Station: {sample_station}")
        if sample_station in self.station_percentiles:
            p = self.station_percentiles[sample_station]
            print(f"  P33 (Low/Mid boundary): {p['p33']:.1f} people")
            print(f"  P66 (Mid/High boundary): {p['p66']:.1f} people")
            print(f"  Range: {p['min']:.1f} ~ {p['max']:.1f} people")

        sample_weekday = "2"  # Wednesday
        if sample_weekday in self.data[sample_station]:
            print(f"  Wednesday (weekday=2) sample hours:")
            for hour_str in ["0", "2", "6", "8", "14", "20"]:
                if hour_str in self.data[sample_station][sample_weekday]:
                    data = self.data[sample_station][sample_weekday][hour_str]
                    hour_int = int(hour_str)
                    print(f"    {hour_int:02d}:00 - {data['people']:7.1f} people (level: {data['level']})")
        print("=" * 50 + "\n")

        self.save_to_cache()

    def _generate_sample_data(self):
        """生成示例資料供開發測試 - 包含所有線路的所有站點"""
        # 使用所有定義的站點
        all_stations = list(STATION_LINE_MAPPING.keys())

        self.data = {}
        for station in all_stations:
            station_dict = {}
            for weekday in range(7):
                hours = {}
                # 模擬高峰期（7-9點, 17-19點）和低峰期
                for hour in range(24):
                    if hour in [7, 8, 9, 17, 18, 19]:
                        people = 3000 + np.random.randint(-500, 500)
                        level = "high"
                    elif hour in [10, 11, 14, 15, 16, 20, 21, 22]:
                        people = 1500 + np.random.randint(-300, 300)
                        level = "medium"
                    else:
                        people = 500 + np.random.randint(-100, 100)
                        level = "low"

                    hours[str(hour)] = {
                        "people": round(max(0, people), 1),
                        "level": level
                    }
                station_dict[str(weekday)] = hours

            # Add line code prefix to station name
            station_with_code = self.get_station_with_line_code(station)
            self.data[station_with_code] = station_dict

        print(f"[OK] Generated {len(self.data)} sample stations")
        self.save_to_cache()

    def get_stations(self):
        """取得所有站點列表"""
        return sorted(list(self.data.keys()))

    def get_congestion(self, station, hour, weekday):
        """取得特定站點、時段、星期幾的壅擠程度"""
        if station not in self.data:
            return None

        if str(weekday) not in self.data[station]:
            return None

        if str(hour) not in self.data[station][str(weekday)]:
            return None

        data = self.data[station][str(weekday)][str(hour)]
        level = data['level']

        # Handle closed stations
        if level == "closed":
            return {
                "station": station,
                "hour": hour,
                "weekday": weekday,
                "people": 0,
                "level": "closed",
                "color": "#999999",
                "label": "未營運",
                "suggestion": "捷運未營運（營運時間 06:00-23:59）",
                "is_operating": False
            }

        return {
            "station": station,
            "hour": hour,
            "weekday": weekday,
            "people": data['people'],
            "level": level,
            "color": CONGESTION_LEVELS[level]["color"],
            "label": CONGESTION_LEVELS[level]["label"],
            "suggestion": self._get_suggestion(level),
            "is_operating": data.get('is_operating', True)
        }

    def _get_suggestion(self, level):
        """依照壅擠程度回傳建議"""
        suggestions = {
            "low": "舒適！現在可以搭乘",
            "medium": "中等壅擠，建議考慮其他時段",
            "high": "非常擁擠，建議選擇其他時段搭乘",
            "closed": "捷運未營運（營運時間 06:00-23:59）"
        }
        return suggestions.get(level, "")

    def get_best_times(self, station, weekday, hour=None, time_range=2, top_n=3):
        """取得該站當天最不擠的時段，或指定時段前後N小時內最不擠的時段

        Args:
            station: 站點名稱
            weekday: 星期幾 (0-6)
            hour: 可選，指定的小時 (0-23)
            time_range: 時間範圍 (小時數)，預設 2，可選 1 或 3
            top_n: 返回前 N 個最不擠的時段，預設 3
        """
        if station not in self.data:
            return []

        if str(weekday) not in self.data[station]:
            return []

        hours = self.data[station][str(weekday)]

        # 決定時段範圍（營運時間 06:00-23:59）
        if hour is not None:
            # 前後 N 小時範圍，但限制在營運時間內
            start_hour = max(6, hour - time_range)
            end_hour = min(23, hour + time_range)
            hour_range = set(range(start_hour, end_hour + 1))
        else:
            # 全天營運時間
            hour_range = set(range(6, 24))

        # 篩選時段範圍內且非未營運的時段
        filtered_hours = [
            (int(h_str), data) for h_str, data in hours.items()
            if int(h_str) in hour_range and data['level'] != 'closed'
        ]

        # 按人次排序，取最少的時段
        sorted_hours = sorted(
            filtered_hours,
            key=lambda x: x[1]['people']
        )

        result = []
        for hour_int, data in sorted_hours[:top_n]:
            result.append({
                "hour": hour_int,
                "people": data['people'],
                "level": data['level'],
                "label": CONGESTION_LEVELS[data['level']]["label"]
            })

        return result

    def get_daily_trend(self, station, weekday):
        """取得該站全天 24 小時的壅擁趨勢"""
        if station not in self.data:
            return []

        if str(weekday) not in self.data[station]:
            return []

        hours = self.data[station][str(weekday)]
        trend = []

        for hour in range(24):
            if str(hour) in hours:
                data = hours[str(hour)]

                # Force non-operating hours (0-5) to be marked as closed
                if hour < 6:
                    trend.append({
                        "hour": hour,
                        "people": 0,
                        "level": "closed",
                        "color": CONGESTION_LEVELS["closed"]["color"]
                    })
                else:
                    trend.append({
                        "hour": hour,
                        "people": data['people'],
                        "level": data['level'],
                        "color": CONGESTION_LEVELS[data['level']]["color"]
                    })

        return trend

# 全域實例
processor = DataProcessor()
