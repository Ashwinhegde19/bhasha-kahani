# Pink Panther - Backend Lead Quick Reference

## 🎯 10-Hour Sprint Mode

**Goal:** Complete backend in 10 hours  
**Focus:** Speed + Quality  
**Read:** `10_HOUR_SPRINT.md` for full timeline

---

## ⚡ Hour-by-Hour Checklist

### Hour 1-2: Foundation
```bash
# Setup (30 min)
cd apps/api
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic httpx python-dotenv

# Models (30 min)
# - User, Story, StoryNode, StoryChoice

# Database (30 min)
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Bulbul Test (30 min)
# - Test API connection
# - Generate 1 sample audio
```

### Hour 3-4: Core APIs
```bash
# Auth endpoint (30 min)
POST /auth/anonymous

# Stories endpoints (60 min)
GET /stories
GET /stories/{slug}

# Choice endpoint (30 min)
POST /stories/{slug}/choices
```

### Hour 5-6: Audio Integration
```bash
# Audio endpoints (60 min)
GET /audio/{node_id}

# Redis caching (30 min)
# - Cache audio metadata

# Audio generation (30 min)
# - Generate 1 story audio
```

### Hour 7-8: Stories + Bulk Audio
```bash
# Write 3 stories (45 min)
# - clever-crow.json
# - kind-woodcutter.json
# - tenali-raman.json

# Bulk generate audio (45 min)
# - All stories
# - All languages
# - Upload to R2

# Progress endpoints (30 min)
GET /users/progress
POST /users/progress
```

### Hour 9-10: Deploy
```bash
# Upload to R2 (30 min)
# - All audio files

# Deploy (90 min)
railway login
railway link
railway up

# Test production API
```

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd bhasha-kahani
git checkout -b feature/PP-sprint

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
DATABASE_URL=postgresql://user:pass@localhost:5432/bhashakahani
REDIS_URL=redis://localhost:6379

R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://xxx.r2.cloudflarestorage.com

SARVAM_API_KEY=xxx
SARVAM_BASE_URL=https://api.sarvam.ai

SECRET_KEY=your-secret-key
```

---

## 📝 Git Commands (10-Hour Sprint)

```bash
# Every 1-2 hours
git add .
git commit -m "[PP] feat: what you built"

# At sync points
git push origin feature/PP-sprint

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

## 🆘 Emergency Help

| Issue | Fix |
|-------|-----|
| Database connection | Check DATABASE_URL, start PostgreSQL |
| Bulbul API 401 | Check SARVAM_API_KEY |
| CORS error | Add CORS middleware in FastAPI |
| Audio not generating | Test Bulbul API directly |
| Deploy failing | Check Railway logs |

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

- [ ] API endpoints work
- [ ] Database migrations run
- [ ] Bulbul generates audio
- [ ] 3 stories in DB
- [ ] All audio uploaded to R2
- [ ] Deployed to Railway

**Full details in 10_HOUR_SPRINT.md**
