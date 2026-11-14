# Deploy SafeRoute on Render (free)

## 1. Push to GitHub
```bash
cd saferoute
git init && git add . && git commit -m "SafeRoute deploy"
git branch -M main
git remote add origin https://github.com/<you>/saferoute.git
git push -u origin main
```
(`.env` is git-ignored – your OpenWeatherMap key is NOT uploaded.)

## 2. Create services from the Blueprint
Render dashboard → **New → Blueprint** → pick the repo → Render reads `render.yaml`
and creates `saferoute-api` (backend) and `saferoute-web` (frontend).
It will ask for 3 values:

| Variable | Service | Value |
|---|---|---|
| `OWM_API_KEY` | saferoute-api | your OpenWeatherMap key (or blank) |
| `CORS_ORIGINS` | saferoute-api | frontend URL, e.g. `https://saferoute-web.onrender.com` |
| `VITE_API_URL` | saferoute-web | backend URL, e.g. `https://saferoute-api.onrender.com` (no trailing slash) |

The URLs are only known after creation. If Render added a suffix to the names, put the real URLs in
afterward (service → Environment). **Changing `VITE_API_URL` needs a redeploy of the frontend**
(Manual Deploy → Clear build cache & deploy) because Vite bakes it in at build time.

## 3. Verify
- `https://<api>.onrender.com/health` → `{"status":"ok"}`
- `https://<api>.onrender.com/docs` → Swagger UI
- Open the frontend: the map should show hotspot markers and prediction should work.

## Notes
- Free web services sleep after ~15 min idle; first request can take ~30–60 s. Open `/health` before a demo.
- The DB is read-only reference data, rebuilt from the CSV at build and again on startup if empty – no Postgres needed.
- Don't upgrade scikit-learn: the `.pkl` models were saved with 1.9.0 (pinned).
