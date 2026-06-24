import React, { useMemo } from 'react';
import './StationSelector.css';

function StationSelector({
  stations,
  stationLines,
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
  // 只顯示 06:00 到 23:59（營運時間）
  const hours = Array.from({ length: 18 }, (_, i) => i + 6);

  // 定義線路資訊（代碼、名稱、emoji）
  const lineInfo = {
    'BR': { name: '文湖線', emoji: '🟤', label: '🟤 棕線' },
    'R': { name: '淡水信義線', emoji: '🔴', label: '🔴 紅線' },
    'G': { name: '松山新店線', emoji: '🟢', label: '🟢 綠線' },
    'O': { name: '中和新蘆線', emoji: '🟠', label: '🟠 橘線' },
    'BL': { name: '板南線', emoji: '🔵', label: '🔵 藍線' },
    'Y': { name: '環狀線', emoji: '🟡', label: '🟡 黃線' }
  };

  const lineOrder = ['BR', 'R', 'G', 'O', 'BL', 'Y'];

  // 根據線路分組站點（純站名）
  const stationsByLine = useMemo(() => {
    console.log('[stationsByLine] 拿到的前10個stations:', stations.slice(0, 10));
    const grouped = {};
    lineOrder.forEach(code => {
      grouped[code] = [];
    });

    // 根據 stationLines 將站點分配到各線路
    stations.forEach(station => {
      if (stationLines[station]) {
        const lines = stationLines[station];
        lines.forEach(lineCode => {
          if (grouped[lineCode]) {
            grouped[lineCode].push(station);
          }
        });
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
      '總計': stations.length
    });

    return grouped;
  }, [stations, stationLines]);

  // 處理線路變更
  const handleLineChange = (e) => {
    const lineCode = e.target.value;
    onLineChange(lineCode);
    // 清除車站選擇
    onStationChange('');
  };

  // 處理車站變更（傳純站名給後端）
  const handleStationChange = (e) => {
    const selectedValue = e.target.value;
    console.log(`[DEBUG] 選擇的車站: ${selectedValue}`);
    onStationChange(selectedValue);
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
              {lineInfo[code].emoji} {lineInfo[code].name}
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
            // 顯示該站所屬的所有線路 emoji 圓點
            const allLines = stationLines[station] || [];
            const lineEmojis = allLines.map(code => lineInfo[code].emoji).join('');
            return (
              <option key={station} value={station}>
                {lineEmojis} {station}
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
