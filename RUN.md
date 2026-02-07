# 🚀 Running Bhasha Kahani

## Quick Start

### Option 1: Run Both Services (Recommended)

```bash
# From the root directory
./start-dev.sh
```

This will start:
- **Backend**: http://localhost:8000 (API + Docs at /docs)
- **Frontend**: http://localhost:3000

### Option 2: Run Services Separately (For Debugging)

**Terminal 1 - Backend:**
```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd apps/web/my-app
npm run dev
```

## 📋 Prerequisites

### Backend Requirements
- Python 3.10+
- PostgreSQL (optional for initial setup - backend will show warnings but work)
- Redis (optional for initial setup)

### Frontend Requirements
- Node.js 20+
- npm or yarn

## ⚙️ Environment Setup

### Backend (.env file)
Located at `apps/api/.env`:

```env
database_url=postgresql://postgres:password@localhost:5432/postgres
redis_url=redis://localhost:6379
sarvam_api_key=your_sarvam_api_key_here
secret_key=local-dev-secret-key-change-in-production
```

**Note:** Backend will start without database, but features requiring DB won't work.

### Frontend (.env.local file)
Located at `apps/web/my-app/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUDIO_CDN=https://audio.bhashakahani.com
NEXT_PUBLIC_IMAGE_CDN=https://cdn.bhashakahani.com
```

## 🔧 Troubleshooting

### Backend Won't Start
1. Check Python version: `python3 --version` (need 3.10+)
2. Reinstall dependencies:
   ```bash
   pip3 install -r apps/api/requirements.txt
   ```
3. Check .env file exists and is properly formatted

### Frontend Won't Start
1. Check Node version: `node --version` (need 20+)
2. Reinstall dependencies:
   ```bash
   cd apps/web/my-app
   npm install
   ```
3. Check .env.local exists

### Port Already in Use
- Backend uses port 8000
- Frontend uses port 3000

Kill processes using these ports:
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

## 📚 Useful URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- API ReDoc: http://localhost:8000/redoc

## 🛑 Stopping the Services

Press `Ctrl+C` in the terminal running `./start-dev.sh`

Or if running separately:
- Press `Ctrl+C` in each terminal
