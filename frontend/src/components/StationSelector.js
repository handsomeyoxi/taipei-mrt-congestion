import React, { useState, useMemo } from 'react';
import './StationSelector.css';

function StationSelector({
  stations,
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

  // 根據站點名稱前綴提取線路代碼
  const extractLineCode = (station) => {
    if (station.startsWith('BR')) return 'BR';
    if (station.startsWith('R')) return 'R';
    if (station.startsWith('G')) return 'G';
    if (station.startsWith('O')) return 'O';
    if (station.startsWith('BL')) return 'BL';
    if (station.startsWith('Y')) return 'Y';
    return null;
  };

  // 根據線路分組站點
  const stationsByLine = useMemo(() => {
    const grouped = {};
    lineOrder.forEach(code => {
      grouped[code] = [];
    });

    stations.forEach(station => {
      const lineCode = extractLineCode(station);
      if (lineCode && grouped[lineCode]) {
        grouped[lineCode].push(station);
      }
    });

    return grouped;
  }, [stations]);

  // 從選定的站點提取線路代碼
  const selectedLine = useMemo(() => {
    return extractLineCode(selectedStation) || '';
  }, [selectedStation]);

  // 處理線路變更
  const handleLineChange = (e) => {
    const lineCode = e.target.value;
    if (lineCode && stationsByLine[lineCode].length > 0) {
      // 自動選擇該線路的第一個站點
      onStationChange(stationsByLine[lineCode][0]);
    }
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
        >
          <option value="">-- 選擇車站 --</option>
          {selectedLine && stationsByLine[selectedLine].map((station) => (
            <option key={station} value={station}>
              {station.substring(extractLineCode(station).length)}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>星期幾</label>
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
