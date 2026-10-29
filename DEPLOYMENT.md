# Sentinel X - Render Deployment Guide

## Prerequisites
- GitHub account with this repo pushed
- Render account (free tier works)

## Step 1: Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click **New** → **PostgreSQL**
3. Name: `sentinel-db`
4. Database: `sentinel`
5. User: `sentinel`
6. Region: Choose closest to you
7. Plan: Free (or Starter for production)
8. Click **Create Database**
9. Copy the **Internal Database URL** (starts with `postgresql://`)

## Step 2: Deploy Backend (Web Service)

1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `sentinel-api`
   - **Root Directory**: `services/sentinel_api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or Starter)

4. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | `postgresql+psycopg2://sentinel:PASSWORD@HOST:5432/sentinel` (from Step 1, change `postgresql://` to `postgresql+psycopg2://`) |
   | `JWT_SECRET` | Generate a random string (e.g., `openssl rand -hex 32`) |
   | `CORS_ORIGINS` | `https://your-frontend.onrender.com` (update after Step 3) |
   | `AI_ENABLED` | `false` (or `true` if you have Ollama key) |
   | `OLLAMA_API_KEY` | Your Ollama Cloud API key (optional) |
   | `OLLAMA_MODEL` | `llama3` (optional) |

5. Click **Create Web Service**
6. Wait for deployment. Note the URL (e.g., `https://sentinel-api.onrender.com`)

## Step 3: Deploy Frontend (Static Site)

### Build locally first:
```bash
cd apps/sentinel_flutter
flutter build web --dart-define=API_BASE_URL=https://sentinel-api.onrender.com
```

### Deploy to Render:
1. Click **New** → **Static Site**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `sentinel-frontend`
   - **Root Directory**: `apps/sentinel_flutter`
   - **Build Command**: `flutter build web --dart-define=API_BASE_URL=https://sentinel-api.onrender.com`
   - **Publish Directory**: `build/web`
4. Click **Create Static Site**

### Alternative: Deploy via Netlify (simpler for Flutter Web):
The project already has `netlify.toml` configured. Just connect the repo to Netlify.

## Step 4: Update CORS

1. Go back to your backend Web Service on Render
2. Update `CORS_ORIGINS` to include your frontend URL:
   `https://sentinel-frontend.onrender.com`
3. Redeploy the backend

## Step 5: Test

1. Open your frontend URL
2. Register a new account
3. Run Global Device Scan
4. Test all features (Reports, Timeline, AI, etc.)

## Notes

- **Free tier limitations**: Render free tier spins down after 15 min of inactivity. First request may take 30-60s.
- **Database**: Free PostgreSQL expires after 90 days. Upgrade to Starter for production.
- **File uploads**: Render's filesystem is ephemeral. Uploaded evidence files won't persist across restarts. For production, use S3 or similar.
- **Canary files**: Stored on the server's filesystem. Won't persist across restarts on free tier.
- **Health check**: Render will hit `/` by default. The app returns `{"app": "Sentinel X API", "version": "0.1.0"}`.

## Troubleshooting

- **500 errors**: Check Render logs. Usually database connection issues.
- **CORS errors**: Make sure `CORS_ORIGINS` includes your frontend URL.
- **Login fails**: Make sure `JWT_SECRET` is set.
- **Slow first load**: Free tier cold start. Upgrade to Starter for always-on.