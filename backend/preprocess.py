#!/usr/bin/env python3
"""
預處理腳本：從台北市開放資料平台下載捷運OD流量數據，並聚合為JSON格式
"""
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from config import CACHE_DIR

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_data_urls():
    """取得捷運OD流量CSV URL（優先API，備用固定URL）"""
    urls = []

    # 方法1: 嘗試台北市開放資料平台API
    try:
        from config import INDEX_CSV_URL
        print(f"[INFO] Attempting Taiwan MRT API: {INDEX_CSV_URL}")
        response = requests.get(INDEX_CSV_URL, timeout=30, verify=False)
        data = response.json()

        if isinstance(data, dict) and 'result' in data and 'results' in data.get('result', {}):
            results = data['result'].get('results', [])
            if results:
                print(f"[DEBUG] Found {len(results)} items in API response")
                for item in results:
                    url = item.get('downloadURL') or item.get('resourceURL') or item.get('url')
                    if url:
                        urls.append(url)

        if urls:
            print(f"[OK] Got {len(urls)} data URLs from API")
            return urls

    except Exception as e:
        print(f"[WARN] API fetch failed: {e}")

    # 方法2: 使用固定的備用 URL（Azure Blob Storage）
    print(f"[INFO] Using fixed backup URLs from Azure Blob Storage")
    urls = [
        "http://tcgmetro.blob.core.windows.net/stationod/臺北捷運每日分時各站OD流量統計資料_202501.csv",
        "http://tcgmetro.blob.core.windows.net/stationod/臺北捷運每日分時各站OD流量統計資料_202412.csv",
        "http://tcgmetro.blob.core.windows.net/stationod/臺北捷運每日分時各站OD流量統計資料_202411.csv",
    ]

    print(f"[OK] Using {len(urls)} backup URLs")
    for i, url in enumerate(urls, 1):
        print(f"     URL {i}: {url[-60:]}")

    return urls

def download_and_process_data():
    """下載並處理捷運OD流量數據"""
    urls = fetch_data_urls()

    if not urls:
        print("[ERROR] Unable to get data URLs")
        return None

    all_data = []

    for i, url in enumerate(urls[:3], 1):  # 取最新3個月
        try:
            print(f"\n[{i}/{min(3, len(urls))}] Downloading: {url[-50:]}")
            response = requests.get(url, timeout=60, verify=False)
            response.encoding = 'utf-8'

            df = pd.read_csv(pd.io.common.StringIO(response.text))
            print(f"     [OK] Downloaded {len(df):,} records")
            all_data.append(df)

        except Exception as e:
            print(f"     [ERROR] Download failed: {str(e)[:80]}")

    if not all_data:
        print("[ERROR] All downloads failed")
        return None

    print(f"\n[INFO] Merging {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"[OK] Total records: {len(combined_df):,}")

    # 清理欄名（移除BOM）
    combined_df.columns = combined_df.columns.str.strip()
    combined_df.columns = [col.replace('﻿', '') for col in combined_df.columns]

    print(f"\n=== Data Diagnostics ===")
    print(f"Columns: {list(combined_df.columns)}")
    print(f"Date range: {combined_df['日期'].min()} to {combined_df['日期'].max()}")
    print(f"Sample rows:")
    print(combined_df[['日期', '時段', '進站', '人次']].head(10).to_string())
    print(f"========================\n")

    return combined_df

def aggregate_data(df):
    """聚合數據為 {站名: {weekday: {hour: {people: N}}}} 格式"""
    if df is None or len(df) == 0:
        return None

    print("[INFO] Parsing dates...")
    try:
        df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
    except:
        try:
            df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')
        except:
            df['日期'] = pd.to_datetime(df['日期'], format='mixed')

    df['weekday'] = df['日期'].dt.weekday.astype('int8')
    df['時段'] = df['時段'].astype('int8')

    # 只保留必要欄位以節省內存
    df = df[['進站', '時段', 'weekday', '日期', '人次']]

    print("[INFO] Grouping by station/hour/weekday/date...")
    daily = df.groupby(['進站', '時段', 'weekday', '日期'])['人次'].sum().reset_index()
    daily.columns = ['station', 'hour', 'weekday', 'date', 'daily_total']

    del df
    import gc
    gc.collect()

    print("[INFO] Calculating daily averages...")
    grouped = daily.groupby(['station', 'hour', 'weekday'])['daily_total'].mean().reset_index()
    grouped.columns = ['station', 'hour', 'weekday', 'avg_people']

    del daily
    gc.collect()

    print(f"[OK] Aggregated {len(grouped):,} records across {grouped['station'].nunique()} stations")

    # 組織為最終格式
    result = {}

    for station in grouped['station'].unique():
        station_data = grouped[grouped['station'] == station]
        station_dict = {}

        for weekday in range(7):
            weekday_data = station_data[station_data['weekday'] == weekday]
            hours_dict = {}

            for _, row in weekday_data.iterrows():
                hour = int(row['hour'])
                people = round(row['avg_people'], 1)
                hours_dict[str(hour)] = {"people": people}

            # 填補缺失的小時
            for h in range(24):
                if str(h) not in hours_dict:
                    # 使用該站點該日期的平均值
                    station_avg = station_data[station_data['weekday'] == weekday]['avg_people'].mean()
                    hours_dict[str(h)] = {"people": round(station_avg if not pd.isna(station_avg) else 0, 1)}

            station_dict[str(weekday)] = hours_dict

        result[station] = station_dict

    print(f"[OK] Generated data for {len(result)} stations")

    # 統計信息
    print(f"\n=== Station Statistics ===")
    station_list = sorted(result.keys())
    print(f"Total stations: {len(station_list)}")
    print(f"Sample stations: {station_list[:5]}")
    print(f"=======================\n")

    return result

def save_json(data, output_path):
    """保存JSON檔案"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        file_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"[OK] Saved to: {output_path}")
        print(f"     File size: {file_size:.2f} MB")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save JSON: {e}")
        return False

def main():
    print("=" * 60)
    print("台北捷運OD流量數據預處理")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Download data
    print("\n[STEP 1] Downloading data from Taiwan MRT API...")
    df = download_and_process_data()

    if df is None or len(df) == 0:
        print("[FATAL] Failed to download data")
        return False

    # Step 2: Aggregate data
    print("\n[STEP 2] Aggregating data...")
    aggregated_data = aggregate_data(df)

    if aggregated_data is None:
        print("[FATAL] Failed to aggregate data")
        return False

    # Step 3: Save to JSON
    print("\n[STEP 3] Saving to JSON...")
    output_path = os.path.join(CACHE_DIR, "preprocessed_data.json")
    if not save_json(aggregated_data, output_path):
        return False

    print("\n" + "=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
