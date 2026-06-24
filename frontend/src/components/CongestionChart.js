import React from 'react';
import './CongestionChart.css';

function CongestionChart({ data, station, stationLines, weekday }) {
  const colorMap = {
    green: '#22c55e',
    yellow: '#eab308',
    red: '#ef4444',
    closed: '#cccccc'
  };

  const lineShortNames = {
    'BR': '棕',
    'R': '紅',
    'G': '綠',
    'O': '橘',
    'BL': '藍',
    'Y': '黃'
  };

  const getStationDisplayName = (stationName) => {
    // stationName 是純站名，從 stationLines 中取得線路資訊
    const lines = stationLines[stationName] || [];
    if (lines.length === 0) return stationName;

    // 顯示所有線路標籤
    const lineLabels = lines.map(code => `[${lineShortNames[code]}]`).join('');
    return `${lineLabels} ${stationName}`;
  };

  // 計算 Y 軸範圍 (加 20% 的上邊界以便顯示)
  const maxPeople = data.length > 0 ? Math.max(...data.map(d => d.people)) : 0;
  const yAxisMax = Math.ceil(maxPeople * 1.2 / 500) * 500; // 四捨五入到 500
  const yStep = Math.ceil(yAxisMax / 4);

  return (
    <div className="chart-card">
      <h3>📊 {getStationDisplayName(station)} - {weekday} 全天趨勢</h3>

      <div className="chart-wrapper">
        <div className="y-axis">
          {[yAxisMax, yAxisMax * 0.75, yAxisMax * 0.5, yAxisMax * 0.25, 0].map((value, idx) => (
            <div key={idx} className="y-label">
              {Math.round(value)}
            </div>
          ))}
        </div>

        <div className="bars-container">
          {/* 網格線 */}
          <div className="grid-lines">
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => (
              <div key={idx} className="grid-line" style={{ bottom: `${ratio * 100}%` }} />
            ))}
          </div>

          {/* 柱狀圖 */}
          {data.map((item, index) => {
            const height = (item.people / yAxisMax) * 100;
            return (
              <div key={index} className="bar-wrapper">
                <div
                  className="bar"
                  style={{
                    height: `${height}%`,
                    backgroundColor: colorMap[item.color]
                  }}
                  title={`${String(item.hour).padStart(2, '0')}:00 - ${Math.round(item.people)} 人`}
                />
                <div className="bar-label">{String(item.hour).padStart(2, '0')}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="chart-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#22c55e' }}></div>
          <span>低擁擠</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#eab308' }}></div>
          <span>中擁擠</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#ef4444' }}></div>
          <span>高擁擠</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#cccccc' }}></div>
          <span>未營運</span>
        </div>
      </div>
    </div>
  );
}

export default CongestionChart;
