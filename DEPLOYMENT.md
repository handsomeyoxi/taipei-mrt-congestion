# 台北捷運壅擠度預測 - 部署指南

## 📋 部署概述

本專案包括：
- **前端**: React 應用 → 部署到 Vercel
- **後端**: FastAPI 應用 → 部署到 Render

## 🚀 前端部署（Vercel）

### 步驟 1: 連接 GitHub 倉庫

1. 訪問 [Vercel](https://vercel.com)
2. 使用 GitHub 帳號登入
3. 點擊 "New Project"
4. 選擇此 GitHub 倉庫 `handsomeyoxi/taipei-mrt-congestion`
5. 設定專案設置：
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 步驟 2: 設定環境變數

在 Vercel 專案設定中，添加環境變數：

```
REACT_APP_API_BASE=https://taipei-mrt-backend.onrender.com
```

### 步驟 3: 部署

- 點擊 "Deploy"
- 等待部署完成（通常 2-5 分鐘）
- 訪問自動生成的 URL（通常是 `https://taipei-mrt-congestion.vercel.app`）

## 🔧 後端部署（Render）

### 步驟 1: 創建 Web Service

1. 訪問 [Render](https://render.com)
2. 使用 GitHub 帳號登入
3. 點擊 "New +"
4. 選擇 "Web Service"
5. 連接此 GitHub 倉庫

### 步驟 2: 配置 Web Service

填寫以下信息：

| 欄位 | 值 |
|------|-----|
| **Name** | `taipei-mrt-backend` |
| **Environment** | `Python 3` |
| **Region** | 選擇離用戶最近的區域（例：Singapore） |
| **Branch** | `master` |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:8000 main:app` |
| **Plan** | Free (或 Starter 以獲得更好的性能) |

### 步驟 3: 設定環境變數

在 Render 環境設定中，不需要額外的環境變數（使用默認值）

### 步驟 4: 部署

- 點擊 "Create Web Service"
- 等待首次部署（通常 3-10 分鐘）
- 部署完成後，獲得 URL（通常是 `https://taipei-mrt-backend.onrender.com`）

## ✅ 驗證部署

### 檢查後端

訪問後端 API 端點：
```
https://taipei-mrt-backend.onrender.com/
```

應該看到：
```json
{
  "message": "台北捷運壅擠度預測 API",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

### 檢查前端

訪問前端：
```
https://taipei-mrt-congestion.vercel.app
```

應該看到：
- 完整的台北捷運壅擠度預測界面
- 能夠選擇車站、日期、時間
- 實時顯示拥挤度和推薦時段

## 📊 監控和維護

### Vercel

- **日誌**: 在 Vercel 專案頁面查看 Function Logs
- **分析**: 查看部署分析和性能指標
- **自動部署**: 推送到 GitHub master 分支會自動部署

### Render

- **日誌**: 在 Render Web Service 頁面查看 Logs
- **監控**: 查看服務的 CPU 和記憶體使用情況
- **自動部署**: 推送到 GitHub master 分支會自動部署

## 🔗 應用 URL

部署完成後：

- **前端**: https://taipei-mrt-congestion.vercel.app
- **後端 API**: https://taipei-mrt-backend.onrender.com
- **API 文檔**: https://taipei-mrt-backend.onrender.com/docs

## 🐛 常見問題

### 問題：前端無法連接後端

**解決**: 確保：
1. 後端 URL 在前端環境變數中正確設定
2. 後端 CORS 設定允許前端的來源
3. 後端已成功部署並運行

### 問題：Render 上的後端啟動很慢

**原因**: 免費層會在不活躍時進入休眠
**解決**: 升級到 Starter 方案或設定定時任務保持活躍

### 問題：數據加載錯誤

**解決**: 
1. 檢查後端日誌
2. 確認本地 CSV 文件是否存在
3. 檢查 Pandas 和 NumPy 版本兼容性

## 📝 更新部署

### 更新前端

```bash
git push origin master
# Vercel 會自動部署
```

### 更新後端

```bash
git push origin master
# Render 會自動部署
```

## 🎉 部署完成！

應用現已對公眾開放，任何人都可以通過公開 URL 訪問和使用。

祝部署順利！
