import React from 'react';
import './StationSelector.css';

function StationSelector({
  stations,
  selectedStation,
  onStationChange,
  selectedWeekday,
  onWeekdayChange,
  selectedHour,
  onHourChange,
  weekdayNames
}) {
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="selector-container">
      <div className="selector-group">
        <label>車站</label>
        <select
          value={selectedStation}
          onChange={(e) => onStationChange(e.target.value)}
          className="selector-input select-large"
        >
          <option value="">-- 選擇車站 --</option>
          {stations.map((station) => (
            <option key={station} value={station}>
              {station}
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
    </div>
  );
}

export default StationSelector;
