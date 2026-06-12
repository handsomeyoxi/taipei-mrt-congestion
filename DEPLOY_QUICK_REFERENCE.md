# 🚀 快速部署參考

## 前端部署（Vercel）- 3 分鐘

```
1. https://vercel.com → Import Project
2. 選擇: handsomeyoxi/taipei-mrt-congestion
3. Framework: Create React App
4. Root Directory: frontend
5. Environment: REACT_APP_API_BASE = https://taipei-mrt-backend.onrender.com
6. Deploy
```

**結果**: `https://taipei-mrt-congestion.vercel.app`

---

## 後端部署（Render）- 5 分鐘

```
1. https://render.com → New Web Service
2. 連接 GitHub: handsomeyoxi/taipei-mrt-congestion
3. 配置:
   - Name: taipei-mrt-backend
   - Environment: Python 3
   - Root Directory: backend
   - Build: pip install -r requirements.txt
   - Start: gunicorn -w 4 -b 0.0.0.0:8000 main:app
4. Create
```

**結果**: `https://taipei-mrt-backend.onrender.com`

---

## ✅ 驗證

| 檢查項 | URL |
|--------|-----|
| **前端** | https://taipei-mrt-congestion.vercel.app |
| **後端** | https://taipei-mrt-backend.onrender.com |
| **API 文檔** | https://taipei-mrt-backend.onrender.com/docs |

---

## 🔄 更新

推送到 GitHub master → 自動部署到 Vercel 和 Render

```bash
git push origin master
```

---

## 📝 環境變數

### Vercel
```
REACT_APP_API_BASE=https://taipei-mrt-backend.onrender.com
```

### Render
（無需設定，使用默認值）

---

## 📁 關鍵文件

| 文件 | 用途 |
|------|------|
| `frontend/vercel.json` | Vercel 配置 |
| `backend/render.yaml` | Render 配置 |
| `.env.production` | 生產環境變數 |
| `requirements.txt` | 後端依賴（含 gunicorn） |

---

## 🆘 故障排查

### 前端無法連接後端
→ 檢查 `.env.production` 中的 API URL

### Render 應用很慢
→ Free 層會進入休眠，考慮升級到 Starter

### 部署失敗
→ 檢查 GitHub Actions 日誌 / Vercel/Render 的構建日誌

---

## 📊 預期服務質量

| 方面 | 免費層 | 升級後 |
|------|--------|--------|
| **Vercel** | ✅ 生產就緒 | ✅ 更快 |
| **Render** | ⚠️ 可能休眠 | ✅ 24/7 運行 |

---

**🎉 部署完成後，應用將對全世界開放！**
