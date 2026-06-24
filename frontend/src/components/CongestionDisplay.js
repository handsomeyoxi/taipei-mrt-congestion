import React from 'react';
import './CongestionDisplay.css';

function CongestionDisplay({ congestion, stationLines, weekdayName, bestTimes, weekdayNames }) {
  const colorMap = {
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
    closed: '#666666'
  };

  const labelMap = {
    low: '低',
    medium: '中',
    high: '高',
    closed: '未營運'
  };

  const lineEmojis = {
    'BR': '🟤',
    'R': '🔴',
    'G': '🟢',
    'O': '🟠',
    'BL': '🔵',
    'Y': '🟡'
  };

  const getStationDisplayName = (stationName) => {
    // stationName 是純站名，從 stationLines 中取得線路資訊
    const lines = stationLines[stationName] || [];
    if (lines.length === 0) return stationName;

    // 顯示所有線路 emoji 圓點
    const emojis = lines.map(code => lineEmojis[code]).join('');
    return `${emojis} ${stationName}`;
  };

  return (
    <div className="congestion-container">
      {/* 主擁擠程度顯示 */}
      <div className="congestion-main-card">
        <div className="congestion-info">
          <h2>{getStationDisplayName(congestion.station)}</h2>
          <p className="time-info">
            {weekdayName} {String(congestion.hour).padStart(2, '0')}:00
          </p>
        </div>

        <div
          className="congestion-display"
          style={{ backgroundColor: colorMap[congestion.color] }}
        >
          <div className="congestion-level">{labelMap[congestion.level]}</div>
          <div className="congestion-label">擁擠度</div>
        </div>

        <div className="congestion-stats">
          <div className="stat">
            <span className="stat-label">平均進站人次</span>
            <span className="stat-value">{Math.round(congestion.people)}</span>
          </div>
        </div>

        <div className="suggestion">
          <span className="suggestion-icon">💡</span>
          {congestion.suggestion}
        </div>
      </div>

      {/* 建議搭車時段 */}
      {bestTimes.length > 0 && (
        <div className="best-times-card">
          <h3>✨ 推薦搭車時段 ({weekdayName})</h3>
          <p className="subtitle">鄰近時段中較不擁擠的推薦</p>

          <div className="best-times-list">
            {bestTimes.map((time, index) => (
              <div
                key={index}
                className="best-time-item"
                style={{
                  borderLeft: `4px solid ${colorMap[time.level]}`
                }}
              >
                <div className="best-time-hour">
                  {String(time.hour).padStart(2, '0')}:00
                </div>
                <div className="best-time-stats">
                  <span className="best-time-people">
                    {Math.round(time.people)} 人
                  </span>
                  <span
                    className="best-time-level"
                    style={{ color: colorMap[time.level] }}
                  >
                    {time.label}擁擠
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CongestionDisplay;
