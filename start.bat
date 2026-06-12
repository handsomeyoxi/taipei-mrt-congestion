@echo off
echo ============================================
echo   台北捷運壅擠度預測 - 啟動腳本
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python！
    echo 請先安裝 Python 3.8 或以上版本
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Node.js！
    echo 請先安裝 Node.js 14 或以上版本
    pause
    exit /b 1
)

echo ✅ 檢測到 Python 和 Node.js
echo.

REM Start backend
echo 🚀 啟動後端伺服器...
start cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo 🚀 啟動前端伺服器...
start cmd /k "cd frontend && npm install && npm start"

echo.
echo ============================================
echo ✨ 應用程式啟動中...
echo ✨ 後端: http://localhost:8000
echo ✨ 前端: http://localhost:3000
echo ✨ API 文件: http://localhost:8000/docs
echo ============================================
echo.
echo 🛑 關閉任一個視窗即可停止應用程式
pause
