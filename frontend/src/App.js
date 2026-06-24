import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StationSelector from './components/StationSelector';
import CongestionDisplay from './components/CongestionDisplay';
import CongestionChart from './components/CongestionChart';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [stations, setStations] = useState([]);
  const [stationLines, setStationLines] = useState({});
  const [selectedLine, setSelectedLine] = useState('');
  const [selectedStation, setSelectedStation] = useState('');
  const [selectedHour, setSelectedHour] = useState(8);
  const [selectedWeekday, setSelectedWeekday] = useState(0);
  const [selectedTimeRange, setSelectedTimeRange] = useState(2);
  const [congestion, setCongestion] = useState(null);
  const [bestTimes, setBestTimes] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const weekdayNames = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'];

  // 取得所有站點
  useEffect(() => {
    const fetchStations = async () => {
      try {
        const response = await axios.get(`${API_BASE}/stations`);
        console.log('[fetchStations] 拿到的前10個stations:', response.data.stations.slice(0, 10));
        console.log('[fetchStations] station_lines 範例:', { 板橋: response.data.station_lines['板橋'], 南勢角: response.data.station_lines['南勢角'] });
        setStations(response.data.stations);
        setStationLines(response.data.station_lines);
      } catch (err) {
        setError('無法載入站點資料');
        console.error(err);
      }
    };
    fetchStations();
  }, []);

  // 查詢擁擠度和建議時段
  const handleQuery = async () => {
    if (!selectedStation) {
      setError('請選擇車站');
      return;
    }

    setLoading(true);
    setError('');
    try {
      // 並行查詢三個 API
      const [congestionRes, bestTimesRes, trendRes] = await Promise.all([
        axios.get(`${API_BASE}/congestion`, {
          params: {
            station: selectedStation,
            hour: selectedHour,
            weekday: selectedWeekday
          }
        }),
        axios.get(`${API_BASE}/best-time`, {
          params: {
            station: selectedStation,
            weekday: selectedWeekday,
            hour: selectedHour,
            time_range: selectedTimeRange
          }
        }),
        axios.get(`${API_BASE}/trend`, {
          params: {
            station: selectedStation,
            weekday: selectedWeekday
          }
        })
      ]);

      setCongestion(congestionRes.data);
      setBestTimes(bestTimesRes.data.best_times);
      setTrendData(trendRes.data.trend);
    } catch (err) {
      setError('查詢失敗，請檢查參數');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 當站點、時段、星期幾或時間範圍改變時自動查詢
  useEffect(() => {
    if (selectedStation) {
      handleQuery();
    }
  }, [selectedStation, selectedHour, selectedWeekday, selectedTimeRange]);

  return (
    <div className="app">
      <header className="header">
        <h1>🚇 台北捷運擁擠度預測</h1>
        <p>找到最舒適的搭車時間</p>
      </header>

      <div className="container">
        <div className="controls">
          <StationSelector
            stations={stations}
            stationLines={stationLines}
            selectedLine={selectedLine}
            onLineChange={setSelectedLine}
            selectedStation={selectedStation}
            onStationChange={setSelectedStation}
            selectedWeekday={selectedWeekday}
            onWeekdayChange={setSelectedWeekday}
            selectedHour={selectedHour}
            onHourChange={setSelectedHour}
            selectedTimeRange={selectedTimeRange}
            onTimeRangeChange={setSelectedTimeRange}
            weekdayNames={weekdayNames}
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">載入中...</div>
        ) : (
          <>
            {congestion && (
              <CongestionDisplay
                congestion={congestion}
                weekdayName={weekdayNames[selectedWeekday]}
                bestTimes={bestTimes}
                weekdayNames={weekdayNames}
              />
            )}

            {trendData.length > 0 && (
              <CongestionChart
                data={trendData}
                station={selectedStation}
                weekday={weekdayNames[selectedWeekday]}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
