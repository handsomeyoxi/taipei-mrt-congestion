import os
import json
import requests
import pandas as pd
import numpy as np
from config import CACHE_DIR, CONGESTION_LEVELS
from datetime import datetime

os.makedirs(CACHE_DIR, exist_ok=True)

class DataProcessor:
    def __init__(self):
        self.cache_file = os.path.join(CACHE_DIR, "congestion_data.json")
        self.stations_file = os.path.join(CACHE_DIR, "stations.json")
        self.data = {}
        self.station_percentiles = {}  # Store P33/P66 for each station
        self.load_from_cache()

    def load_from_cache(self):
        """From cache load data"""
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
            print(f"[OK] Data cached: {self.cache_file}")
        except Exception as e:
            print(f"[ERROR] Cache save failed: {e}")

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
        """Get data URLs from index CSV"""
        try:
            from config import INDEX_CSV_URL
            response = requests.get(INDEX_CSV_URL, timeout=10)
            response.encoding = 'utf-8'

            # Parse JSON response
            data = response.json()
            urls = []

            if 'result' in data and 'results' in data['result']:
                for item in data['result']['results']:
                    if 'resourceURL' in item:
                        urls.append(item['resourceURL'])

            print(f"[OK] Got {len(urls)} data URLs")
            return urls
        except Exception as e:
            print(f"[ERROR] Index CSV fetch failed: {e}")
            return []

    def download_and_parse_data(self, urls=None, csv_path=None, months=1):
        """Download and parse monthly data"""
        # Use local index CSV if provided
        if csv_path and os.path.exists(csv_path):
            print(f"[INFO] Reading local index CSV: {csv_path}")
            urls = self.fetch_index_csv_local(csv_path, months=months)

        if urls is None or len(urls) == 0:
            print("[WARN] Unable to get data URLs, using sample data")
            self._generate_sample_data()
            return

        all_data = []
        for i, url in enumerate(urls, 1):
            try:
                print(f"[{i}/{len(urls)}] Downloading: {url[-30:]}")
                response = requests.get(url, timeout=30)
                response.encoding = 'utf-8'
                df = pd.read_csv(pd.io.common.StringIO(response.text))
                all_data.append(df)
                print(f"     [OK] Parsed {len(df):,} records")
            except Exception as e:
                print(f"     [ERROR] Download failed: {str(e)[:50]}")

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"[OK] Merged data: {len(combined_df):,} total records")
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
        """Process DataFrame and calculate statistics"""
        # Ensure column names are clean and handle BOM
        df.columns = df.columns.str.strip()
        df.columns = [col.replace('﻿', '') for col in df.columns]  # Remove BOM

        print(f"\n=== After BOM removal ===")
        print(f"Column names: {list(df.columns)}")
        print(f"Sample row: {df.iloc[0].to_dict()}")
        print(f"============================\n")

        # Parse date - handle both formats (YYYYMMDD and YYYY-MM-DD)
        try:
            df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
        except:
            try:
                df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
            except:
                df['日期'] = pd.to_datetime(df['日期'], format='mixed')

        df['weekday'] = df['日期'].dt.weekday
        df['時段'] = df['時段'].astype(int)

        # Group by [station, hour, weekday]
        # First: sum all destinations for each station/hour/weekday/date
        daily = df.groupby(['進站', '時段', 'weekday', '日期'])['人次'].sum().reset_index()
        daily.columns = ['station', 'hour', 'weekday', 'date', 'daily_total']

        # Second: average across all dates
        grouped = daily.groupby(['station', 'hour', 'weekday'])['daily_total'].mean().reset_index()
        grouped.columns = ['station', 'hour', 'weekday', 'avg_people']

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

            # Store the percentiles for this station
            self.station_percentiles[station] = {
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

            self.data[station] = station_dict

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
        """生成示例資料供開發測試"""
        stations = [
            "台北車站", "中山", "台北101/世貿", "信義安和",
            "象山", "南港軟體園區", "南港展覽館", "昆陽",
            "後山埤", "永春", "府中", "新埤"
        ]

        self.data = {}
        for station in stations:
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
            self.data[station] = station_dict

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

    def get_best_times(self, station, weekday, hour=None, top_n=3):
        """取得該站當天最不擠的時段，或指定時段前後2小時內最不擠的時段"""
        if station not in self.data:
            return []

        if str(weekday) not in self.data[station]:
            return []

        hours = self.data[station][str(weekday)]

        # 決定時段範圍（營運時間 06:00-23:59）
        if hour is not None:
            # 前後2小時範圍，但限制在營運時間內
            start_hour = max(6, hour - 2)
            end_hour = min(23, hour + 2)
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
        """取得該站全天 24 小時的壅擠趨勢"""
        if station not in self.data:
            return []

        if str(weekday) not in self.data[station]:
            return []

        hours = self.data[station][str(weekday)]
        trend = []

        for hour in range(24):
            if str(hour) in hours:
                data = hours[str(hour)]
                trend.append({
                    "hour": hour,
                    "people": data['people'],
                    "level": data['level'],
                    "color": CONGESTION_LEVELS[data['level']]["color"]
                })

        return trend

# 全域實例
processor = DataProcessor()
