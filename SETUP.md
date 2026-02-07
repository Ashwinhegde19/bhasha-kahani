# Bhasha Kahani - Setup Guide

## 🚀 Quick Start

This guide will help you set up the Bhasha Kahani project locally and deploy it to production.

---

## 📋 Prerequisites

### Required Software

| Software | Version | Install Link |
|----------|---------|--------------|
| Node.js | 18+ | [Download](https://nodejs.org/) |
| Python | 3.9+ | [Download](https://python.org/) |
| Git | Latest | [Download](https://git-scm.com/) |
| PostgreSQL | 14+ | [Download](https://postgresql.org/) |

### Accounts Needed

- [GitHub](https://github.com/)
- [Vercel](https://vercel.com/) (Frontend hosting)
- [Railway](https://railway.app/) (Backend + Database)
- [Cloudflare](https://cloudflare.com/) (R2 Storage)
- [Upstash](https://upstash.com/) (Redis)
- [Sentry](https://sentry.io/) (Error tracking)
- [Sarvam AI](https://sarvam.ai/) (Bulbul API)

---

## 🛠️ Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/bhasha-kahani.git
cd bhasha-kahani
```

### Step 2: Setup Backend

```bash
# Navigate to backend
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Backend .env:**
```env
# Database (Local)
DATABASE_URL=postgresql://postgres:password@localhost:5432/bhashakahani

# Redis (Local or Upstash)
REDIS_URL=redis://localhost:6379

# Cloudflare R2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://your-account.r2.cloudflarestorage.com

# Sarvam Bulbul
SARVAM_API_KEY=your_sarvam_api_key
SARVAM_BASE_URL=https://api.sarvam.ai

# Security
SECRET_KEY=your-super-secret-key-change-this

# Sentry (Optional for local)
SENTRY_DSN=
```

### Step 3: Setup Database

```bash
# Create database
createdb bhashakahani

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_stories.py
```

### Step 4: Run Backend

```bash
# Development server
uvicorn app.main:app --reload --port 8000

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 5: Setup Frontend

```bash
# Navigate to frontend
cd apps/web

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**Frontend .env.local:**
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_OFFLINE=true

# App Config
NEXT_PUBLIC_APP_NAME=Bhasha Kahani
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Step 6: Run Frontend

```bash
# Development server
npm run dev

# App will be available at http://localhost:3000
```

---

## 🗄️ Database Setup (Railway)

### Option 1: Railway PostgreSQL (Recommended)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Provision PostgreSQL"
4. Copy the `DATABASE_URL` from Variables
5. Add to your backend `.env`

### Option 2: Supabase

1. Go to [Supabase](https://supabase.com/)
2. Create new project
3. Go to Settings > Database
4. Copy connection string
5. Add to your backend `.env`

---

## 💾 Cloudflare R2 Setup

### Create Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to R2
3. Click "Create bucket"
4. Name: `bhashakahani-audio`
5. Region: Auto

### Get API Credentials

1. Go to R2 > Manage R2 API Tokens
2. Click "Create API Token"
3. Permissions: Object Read & Write
4. Copy:
   - Account ID
   - Access Key ID
   - Secret Access Key

### Configure Public Access

1. Go to bucket settings
2. Enable "Allow public access"
3. Note the public URL

---

## ⚡ Upstash Redis Setup

1. Go to [Upstash Console](https://console.upstash.com/)
2. Click "Create Database"
3. Name: `bhashakahani`
4. Region: Same as your backend
5. Copy the `REDIS_URL`
6. Add to your backend `.env`

---

## 🔑 Sarvam API Key

1. Go to [Sarvam AI](https://sarvam.ai/)
2. Sign up / Log in
3. Go to Dashboard > API Keys
4. Generate new API key
5. Copy and add to `.env`

---

## 🚀 Deployment

### Deploy Backend to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Get production URL
railway domain
```

### Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Or connect GitHub repo for auto-deploy
```

### Configure Environment Variables (Production)

**Railway (Backend):**
```
DATABASE_URL=your_railway_postgres_url
REDIS_URL=your_upstash_redis_url
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://audio.bhashakahani.com
SARVAM_API_KEY=xxx
SECRET_KEY=xxx
SENTRY_DSN=xxx
```

**Vercel (Frontend):**
```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
NEXT_PUBLIC_SENTRY_DSN=xxx
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_OFFLINE=true
```

---

## 🧪 Testing

### Backend Tests

```bash
cd apps/api

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_stories.py -v
```

### Frontend Tests

```bash
cd apps/web

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run with coverage
npm run test:coverage
```

### Manual Testing Checklist

- [ ] Story gallery loads
- [ ] Story detail page works
- [ ] Audio plays correctly
- [ ] Choices work
- [ ] Language switching works
- [ ] Code-mixing works
- [ ] Progress saves
- [ ] Bookmarks work
- [ ] Offline mode works
- [ ] Mobile responsive

---

## 📦 Useful Commands

### Backend

```bash
# Run development server
uvicorn app.main:app --reload

# Run production server
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Generate audio for story
python scripts/generate_audio.py --story clever-crow --language hi
```

### Frontend

```bash
# Development
npm run dev

# Build
npm run build

# Start production
npm start

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

---

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error

```
Error: connection to server at "localhost" failed
```

**Solution:**
```bash
# Start PostgreSQL
# macOS:
brew services start postgresql

# Linux:
sudo service postgresql start

# Verify connection
psql -U postgres -d bhashakahani
```

#### Redis Connection Error

```
Error: Connection refused
```

**Solution:**
```bash
# Start Redis
redis-server

# Or use Upstash URL instead of local
```

#### Bulbul API Error

```
Error: 401 Unauthorized
```

**Solution:**
- Check SARVAM_API_KEY in .env
- Verify API key is active
- Check API rate limits

#### Audio Not Playing

**Solution:**
```bash
# Check audio file exists
curl -I https://audio.bhashakahani.com/your-audio.mp3

# Check CORS headers
# Add to R2 bucket CORS config
```

---

## 📝 Project Structure Reference

```
bhasha-kahani/
├── apps/
│   ├── web/              # Next.js frontend
│   │   ├── app/          # App router
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── lib/          # Utilities
│   │   ├── store/        # Zustand stores
│   │   └── types/        # TypeScript types
│   │
│   └── api/              # FastAPI backend
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── services/
│       │   ├── models/
│       │   └── schemas/
│       ├── alembic/
│       └── tests/
│
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── .github/
    └── workflows/        # CI/CD
```

---

## 🆘 Getting Help

### Resources

- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Howler.js Docs](https://howlerjs.com/)
- [shadcn/ui Docs](https://ui.shadcn.com/)

### Community

- GitHub Issues: [Report bugs](https://github.com/yourusername/bhasha-kahani/issues)
- Discussions: [Ask questions](https://github.com/yourusername/bhasha-kahani/discussions)

---

## ✅ Setup Checklist

### Local Development
- [ ] Node.js installed
- [ ] Python installed
- [ ] PostgreSQL installed
- [ ] Repository cloned
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database created
- [ ] Migrations run
- [ ] Environment variables configured
- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:3000

### External Services
- [ ] Railway account created
- [ ] Vercel account created
- [ ] Cloudflare R2 bucket created
- [ ] Upstash Redis created
- [ ] Sentry project created
- [ ] Sarvam API key obtained

### Production
- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Production environment variables set
- [ ] Domain configured (optional)
- [ ] SSL enabled
- [ ] Monitoring active

---

**Version:** 1.0  
**Last Updated:** February 7, 2026
