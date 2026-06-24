import React, { useState, useMemo } from 'react';
import './StationSelector.css';

function StationSelector({
  stations,
  selectedLine,
  onLineChange,
  selectedStation,
  onStationChange,
  selectedWeekday,
  onWeekdayChange,
  selectedHour,
  onHourChange,
  selectedTimeRange,
  onTimeRangeChange,
  weekdayNames
}) {
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // 定義線路資訊（代碼、名稱、顏色）
  const lineInfo = {
    'BR': { name: '文湖線', color: '🟤 棕線' },
    'R': { name: '淡水信義線', color: '🔴 紅線' },
    'G': { name: '松山新店線', color: '🟢 綠線' },
    'O': { name: '中和新蘆線', color: '🟠 橘線' },
    'BL': { name: '板南線', color: '🔵 藍線' },
    'Y': { name: '環狀線', color: '🟡 黃線' }
  };

  const lineOrder = ['BR', 'R', 'G', 'O', 'BL', 'Y'];

  const lineEmojis = {
    'BR': '🟤',
    'R': '🔴',
    'G': '🟢',
    'O': '🟠',
    'BL': '🔵',
    'Y': '🟡'
  };

  // 根據站點名稱前綴提取線路代碼
  // 注意：必須先檢查2字符的代碼（BR、BL），再檢查1字符的代碼
  const extractLineCode = (station) => {
    // 2字符線路代碼（必須先檢查）
    if (station.startsWith('BR')) return 'BR';
    if (station.startsWith('BL')) return 'BL';
    // 1字符線路代碼
    if (station.startsWith('R')) return 'R';
    if (station.startsWith('G')) return 'G';
    if (station.startsWith('O')) return 'O';
    if (station.startsWith('Y')) return 'Y';
    // 未知格式，返回 null
    return null;
  };

  // 查找站點屬於的所有線路
  const findAllLines = (stationName) => {
    const lines = [];
    lineOrder.forEach(code => {
      if (stationsByLine[code] && stationsByLine[code].some(s => {
        const lineCode = extractLineCode(s);
        if (!lineCode) return false;
        return s.substring(lineCode.length) === stationName;
      })) {
        lines.push(code);
      }
    });
    return lines;
  };

  // 根據線路分組站點
  const stationsByLine = useMemo(() => {
    const grouped = {};
    lineOrder.forEach(code => {
      grouped[code] = [];
    });

    let unclassifiedCount = 0;
    stations.forEach(station => {
      const lineCode = extractLineCode(station);
      if (lineCode && grouped[lineCode]) {
        grouped[lineCode].push(station);
      } else {
        // 調試：如果站點無法分類，記錄警告
        if (!lineCode) {
          unclassifiedCount++;
          console.warn(`[WARNING] 無法提取線路代碼: ${station}`);
        }
      }
    });

    // 調試：輸出分組統計
    console.log('[INFO] 線路站點統計:', {
      'BR': grouped['BR'].length,
      'R': grouped['R'].length,
      'G': grouped['G'].length,
      'O': grouped['O'].length,
      'BL': grouped['BL'].length,
      'Y': grouped['Y'].length,
      '無法分類': unclassifiedCount,
      '總計': stations.length
    });

    return grouped;
  }, [stations]);

  // 處理線路變更
  const handleLineChange = (e) => {
    const lineCode = e.target.value;
    onLineChange(lineCode);
    // 清除車站選擇
    onStationChange('');
  };

  // 處理車站變更
  const handleStationChange = (e) => {
    onStationChange(e.target.value);
  };

  return (
    <div className="selector-container">
      <div className="selector-group">
        <label>捷運線路</label>
        <select
          value={selectedLine}
          onChange={handleLineChange}
          className="selector-input"
        >
          <option value="">-- 選擇線路 --</option>
          {lineOrder.map((code) => (
            <option key={code} value={code}>
              {lineInfo[code].color} {lineInfo[code].name}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>車站</label>
        <select
          value={selectedStation}
          onChange={handleStationChange}
          className="selector-input select-large"
          disabled={!selectedLine}
        >
          <option value="">
            {selectedLine ? '-- 選擇車站 --' : '-- 請先選擇線路 --'}
          </option>
          {selectedLine && stationsByLine[selectedLine] && stationsByLine[selectedLine].map((station) => {
            const lineCode = extractLineCode(station);
            // 防守性檢查：確保有有效的線路代碼
            if (!lineCode) {
              console.error(`[ERROR] 站點 "${station}" 沒有有效的線路代碼`);
              return null;
            }
            const stationName = station.substring(lineCode.length);
            const allLines = findAllLines(stationName);
            const lineColors = allLines.map(code => lineEmojis[code]).join('');
            return (
              <option key={station} value={station}>
                {lineColors} {stationName}
              </option>
            );
          })}
        </select>
      </div>

      <div className="selector-group">
        <label>星期</label>
        <select
          value={selectedWeekday}
          onChange={(e) => onWeekdayChange(parseInt(e.target.value))}
          className="selector-input"
        >
          {weekdayNames.map((day, index) => (
            <option key={index} value={index}>
              {day}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>時段</label>
        <select
          value={selectedHour}
          onChange={(e) => onHourChange(parseInt(e.target.value))}
          className="selector-input"
        >
          {hours.map((hour) => (
            <option key={hour} value={hour}>
              {String(hour).padStart(2, '0')}:00 - {String(hour).padStart(2, '0')}:59
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>推薦時間範圍</label>
        <div className="time-range-selector">
          {[1, 2, 3].map((range) => (
            <button
              key={range}
              className={`time-range-btn ${selectedTimeRange === range ? 'active' : ''}`}
              onClick={() => onTimeRangeChange(range)}
              title={`顯示當前時段前後 ${range} 小時內最不擁擠的時段`}
            >
              ±{range}h
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StationSelector;
