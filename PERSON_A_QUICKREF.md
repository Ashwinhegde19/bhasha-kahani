# Pink Panther - Backend Lead Quick Reference

## 🎯 Today's Priority
Check `TEAM_COLLABORATION.md` for detailed daily tasks.

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd bhasha-kahani

# 2. Create your feature branch
git checkout develop
git pull origin develop
git checkout -b feature/A-api-setup

# 3. Setup backend
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy env and configure
cp .env.example .env
# Edit .env with your credentials

# 5. Run migrations and start
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

## 📁 You Own These Files

```
apps/api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── stories.py
│   │   ├── audio.py
│   │   ├── users.py
│   │   ├── choices.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── story_service.py
│   │   ├── audio_service.py
│   │   └── bulbul_service.py
│   ├── models/
│   │   ├── story.py
│   │   ├── user.py
│   │   └── progress.py
│   └── schemas/
│       └── *.py
├── alembic/
├── tests/
└── requirements.txt

scripts/
├── seed_stories.py
└── generate_audio.py

packages/shared/ (coordinate with B)
```

---

## 🔑 Key Environment Variables

```env
# Database (Railway or local)
DATABASE_URL=postgresql://...

# Redis (Upstash or local)
REDIS_URL=rediss://...

# Cloudflare R2
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://...

# Sarvam Bulbul
SARVAM_API_KEY=xxx
SARVAM_BASE_URL=https://api.sarvam.ai

# Security
SECRET_KEY=your-secret-key
```

---

## 📝 Daily Checklist

### Morning
- [ ] `git checkout develop && git pull`
- [ ] `git checkout feature/your-branch`
- [ ] `git rebase develop`
- [ ] Review Jackie Chan's overnight PRs

### During Day
- [ ] Commit every 30-60 minutes
- [ ] Use format: `[PP] feat: description`
- [ ] Test endpoints with curl/Postman

### Evening
- [ ] Push branch: `git push origin feature/your-branch`
- [ ] Create PR to `develop`
- [ ] Tag Jackie Chan for review
- [ ] Update task status in TEAM_COLLABORATION.md

---

## 🧪 Testing Your Endpoints

```bash
# Test auth
curl -X POST http://localhost:8000/auth/anonymous

# Test stories list
curl http://localhost:8000/stories

# Test story detail
curl http://localhost:8000/stories/clever-crow
```

---

## 🆘 Emergency Contacts

- **Blocked by API question?** → Ping Jackie Chan
- **Bulbul API issue?** → Check Sarvam dashboard
- **Database error?** → Check Railway logs
- **Can't deploy?** → Check Railway CLI

---

## 📚 Useful Commands

```bash
# Create migration
alembic revision --autogenerate -m "add_user_table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Generate audio
python scripts/generate_audio.py --story clever-crow --language hi

# Deploy to Railway
railway login
railway link
railway up
```

---

**Full details in TEAM_COLLABORATION.md**
