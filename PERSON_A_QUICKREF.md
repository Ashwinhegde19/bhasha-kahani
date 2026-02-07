# Pink Panther - Backend Lead Quick Reference

## 🎯 10-Hour Sprint Mode

**Goal:** Complete backend in 10 hours  
**Focus:** Speed + Quality  
**Read:** `10_HOUR_SPRINT.md` for full timeline

---

## ⚡ Hour-by-Hour Checklist

### Hour 1-2: Foundation ✅ COMPLETED
```bash
# ✅ Setup (30 min) - DONE
# ✅ Models (30 min) - DONE (User, Story, StoryNode, StoryChoice, etc.)
# ✅ Database (30 min) - DONE (Supabase PostgreSQL connected, migrations run)
# ✅ Bulbul Test (30 min) - DONE (API working, generates 255KB+ audio files)
```

### Hour 3-4: Core APIs ✅ COMPLETED
```bash
# ✅ Auth endpoint (30 min) - DONE
POST /auth/anonymous

# ✅ Stories endpoints (60 min) - DONE
GET /stories
GET /stories/{slug}

# ✅ Choice endpoint (30 min) - DONE
GET /choices/{choice_id}
```

### Hour 5-6: Audio Integration ✅ COMPLETED
```bash
# ✅ Audio endpoints (60 min) - DONE
GET /audio/{node_id}

# ✅ Redis caching (30 min) - DONE
# - Cache audio URLs (30-day TTL)

# ✅ Audio generation (30 min) - DONE
# - Generates audio on-the-fly via Bulbul API
# - Uploads to Supabase Storage (R2 alternative)
```

### Hour 7-8: Stories + Storage ✅ COMPLETED
```bash
# ✅ Write 2 stories (45 min) - DONE
# - clever-crow.json
# - punyakoti.json

# ✅ Supabase Storage (45 min) - DONE
# - Audio uploads working
# - Public CDN URLs
# - No credit card needed!

# ✅ User endpoints (30 min) - DONE
GET /users/me
```

### Hour 9-10: Deploy ⏳ IN PROGRESS
```bash
# ✅ Railway config (30 min) - DONE
# - railway.toml
# - Procfile
# - RAILWAY_DEPLOY.md

# ⏳ Deploy (60 min) - PENDING
# - Requires credit card for $5 free credit
# - Alternative: Use Vercel (limited) or Oracle Cloud

# ⏳ Test production API - PENDING
```

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd bhasha-kahani
git checkout -b feature/backend-sprint

# Setup backend
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env

# Start
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## 🔑 Environment Variables (.env)

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres

# Cache
REDIS_URL=redis://localhost:6379

# Storage (Supabase - FREE, no card needed!)
SUPABASE_SERVICE_KEY=your_service_role_key

# Audio Generation (Sarvam Bulbul)
SARVAM_API_KEY=xxx
SARVAM_BASE_URL=https://api.sarvam.ai

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Audio Cache
AUDIO_CACHE_TTL_DAYS=30
```

---

## 📝 Git Commands (10-Hour Sprint)

```bash
# Every 1-2 hours
git add .
git commit -m "[PP] feat: what you built"

# At sync points
git push origin feature/backend-sprint

# Jackie needs your changes?
git checkout develop
git merge feature/PP-sprint
git push origin develop
```

---

## 🧪 Quick Tests

```bash
# Test auth
curl -X POST http://localhost:8000/auth/anonymous

# Test stories
curl http://localhost:8000/stories
curl http://localhost:8000/stories/clever-crow

# Test choice
curl -X POST http://localhost:8000/stories/clever-crow/choices \
  -H "Content-Type: application/json" \
  -d '{"node_id":"xxx","choice_key":"A"}'

# Test audio
curl http://localhost:8000/audio/xxx?language=hi
```

---

## 🏆 Accomplishments

### ✅ What's Working
1. **6 API Endpoints** - All tested locally
2. **2 Stories Seeded** - Clever Crow, Punyakoti
3. **Audio Generation** - Bulbul API produces real audio (255KB+)
4. **Supabase Storage** - Audio files uploaded to CDN (FREE)
5. **JWT Auth** - Anonymous users with 24h tokens
6. **Character/Choice Counts** - Fixed SQL joins
7. **Redis Caching** - 30-day audio URL cache

### 🚀 Deployment Status
- **Local**: ✅ Fully working
- **Railway**: ⏳ Config ready, needs credit card
- **Vercel**: ⚠️ Deployed but DB blocked (serverless limitation)

### 📝 PR Created
**PR #1**: Merge feature/backend-sprint → develop
- All backend code complete
- Ready for Jackie Chan integration

---

## 🆘 Emergency Help

| Issue | Fix |
|-------|-----|
| Database connection | Check DATABASE_URL format, use port 6543 for pooler |
| Bulbul API 401 | Check SARVAM_API_KEY |
| CORS error | Already configured in FastAPI |
| Audio not generating | Test with `python scripts/generate_audio_bulk.py` |
| Deploy failing | Check Railway logs, verify Procfile exists |

---

## 📚 Bulbul API Quick

```python
import httpx

async def generate_audio(text: str, language: str, speaker: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sarvam.ai/v1/speech/generate",
            headers={"API-Subscription-Key": API_KEY},
            json={
                "inputs": [text],
                "target_language_code": language,
                "speaker": speaker,
                "model": "bulbul:v3"
            }
        )
        return response.json()
```

**Speakers:** meera, arvind, pooja, amol, neha, etc.

---

## ✅ Success Checklist

### Backend - COMPLETED ✅
- [x] API endpoints created (6 endpoints)
  - [x] POST /auth/anonymous
  - [x] GET /stories
  - [x] GET /stories/{slug}
  - [x] GET /choices/{choice_id}
  - [x] GET /audio/{node_id}
  - [x] GET /users/me
- [x] Database migrations run (Alembic)
- [x] Supabase PostgreSQL connected
- [x] **Bulbul generates audio** (255KB+ WAV files)
- [x] 2 stories in DB (Clever Crow, Punyakoti)
- [x] **Supabase Storage** for audio (CDN URLs)
- [x] Character/Choice counts working
- [x] JWT authentication implemented
- [x] Redis caching for audio URLs
- [x] Railway deployment config ready

### Deployment - PENDING ⏳
- [ ] Deployed to production
  - Railway: Requires credit card ($5 free credit)
  - Vercel: Deployed but DB connection blocked
  - Alternative: Oracle Cloud (truly free, needs setup)

**Full details in 10_HOUR_SPRINT.md**
