# Bhasha Kahani - Technical Specification

## 📋 Overview

**Bhasha Kahani** is a multilingual interactive folktale storytelling platform powered by Sarvam AI's Bulbul V3. This document provides the complete technical specification for building the application.

---

## 🎯 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15 + TypeScript | React framework with App Router |
| **Styling** | Tailwind CSS + shadcn/ui | Modern UI components |
| **State (Client)** | Zustand | Global state management |
| **State (Server)** | TanStack Query | Server state, caching, sync |
| **Audio** | Howler.js | Cross-browser audio playback |
| **Backend** | FastAPI | Python async API framework |
| **Database** | PostgreSQL | Primary data storage |
| **Audio Storage** | Cloudflare R2 | CDN-optimized audio files |
| **Caching** | Upstash Redis | Session, audio metadata cache |
| **Error Tracking** | Sentry | Production monitoring |
| **Hosting** | Vercel (FE) + Railway (BE) | Deployment |
| **CI/CD** | GitHub Actions | Automated deployment |

**Total Cost: $0/month** ✅

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Next.js 15 (Vercel)                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   App Router │  │  Zustand     │  │ TanStack     │              │   │
│  │  │   (App Dir)  │  │  Store       │  │ Query        │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Howler.js   │  │  shadcn/ui   │  │  PWA SW      │              │   │
│  │  │  Audio       │  │  Components  │  │  (Offline)   │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ HTTPS/REST
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI (Railway)                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Story API   │  │  Audio API   │  │  User API    │              │   │
│  │  │  /stories/*  │  │  /audio/*    │  │  /users/*    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Choice API  │  │  Admin API   │  │  Analytics   │              │   │
│  │  │  /choices/*  │  │  /admin/*    │  │  /analytics/*│              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
│     DATA LAYER        │ │   CACHE LAYER     │ │   EXTERNAL SERVICES   │
│  ┌─────────────────┐  │ │  ┌─────────────┐  │ │  ┌─────────────────┐  │
│  │  PostgreSQL     │  │ │  │   Redis     │  │ │  │  Sarvam Bulbul  │  │
│  │  (Railway/      │  │ │  │  (Upstash)  │  │ │  │     V3 API      │  │
│  │   Supabase)     │  │ │  │             │  │ │  │                 │  │
│  │                 │  │ │  │ - Sessions  │  │ │  │ - TTS Generate  │  │
│  │ - Stories       │  │ │  │ - Audio MD  │  │ │  │ - 35+ Voices    │  │
│  │ - Users         │  │ │  │ - Rate Lim  │  │ │  │ - 11 Languages  │  │
│  │ - Progress      │  │ │  └─────────────┘  │ │  └─────────────────┘  │
│  │ - Analytics     │  │ └───────────────────┘ │  ┌─────────────────┐  │
│  └─────────────────┘  │                       │  │  Cloudflare R2  │  │
└───────────────────────┘                       │  │                 │  │
                                                │  │ - Audio Storage │  │
                                                │  │ - CDN Delivery  │  │
                                                │  └─────────────────┘  │
                                                └───────────────────────┘
```

---

## 📁 Project Structure

```
bhasha-kahani/
├── apps/
│   ├── web/                          # Next.js 15 Frontend
│   │   ├── app/                      # App Router
│   │   │   ├── (main)/               # Main layout group
│   │   │   │   ├── page.tsx          # Home/Language select
│   │   │   │   ├── stories/          # Story gallery
│   │   │   │   ├── play/[id]/        # Story player
│   │   │   │   └── layout.tsx        # Main layout
│   │   │   ├── api/                  # API routes (proxy)
│   │   │   └── layout.tsx            # Root layout
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── story/                # Story-specific components
│   │   │   ├── audio/                # Audio player components
│   │   │   └── layout/               # Layout components
│   │   ├── hooks/                    # Custom hooks
│   │   ├── lib/                      # Utilities
│   │   ├── store/                    # Zustand stores
│   │   ├── types/                    # TypeScript types
│   │   ├── public/                   # Static assets
│   │   └── next.config.js
│   │
│   └── api/                          # FastAPI Backend
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py               # FastAPI app entry
│       │   ├── config.py             # Configuration
│       │   ├── dependencies.py       # DI dependencies
│       │   ├── routers/              # API routers
│       │   │   ├── stories.py        # Story endpoints
│       │   │   ├── audio.py          # Audio endpoints
│       │   │   ├── users.py          # User endpoints
│       │   │   ├── choices.py        # Choice endpoints
│       │   │   ├── admin.py          # Admin endpoints
│       │   │   └── analytics.py      # Analytics endpoints
│       │   ├── services/             # Business logic
│       │   │   ├── story_service.py
│       │   │   ├── audio_service.py
│       │   │   ├── bulbul_service.py
│       │   │   ├── cache_service.py
│       │   │   └── analytics_service.py
│       │   ├── models/               # SQLAlchemy models
│       │   │   ├── story.py
│       │   │   ├── user.py
│       │   │   ├── progress.py
│       │   │   └── analytics.py
│       │   ├── schemas/              # Pydantic schemas
│       │   ├── utils/                # Utilities
│       │   └── workers/              # Background tasks
│       ├── alembic/                  # Database migrations
│       ├── tests/                    # Test suite
│       ├── requirements.txt
│       └── Dockerfile
│
├── packages/
│   └── shared/                       # Shared types/utils
│       ├── src/
│       │   ├── types/
│       │   └── constants/
│       └── package.json
│
├── infra/                            # Infrastructure
│   ├── terraform/                    # IaC (optional)
│   └── docker/                       # Docker configs
│
├── .github/
│   └── workflows/                    # CI/CD pipelines
│       ├── deploy-web.yml
│       └── deploy-api.yml
│
├── docs/                             # Documentation
│   ├── TECH_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API_SPEC.md
│   ├── FRONTEND.md
│   └── ROADMAP.md
│
├── scripts/                          # Utility scripts
│   ├── seed-stories.py
│   ├── generate-audio.py
│   └── setup-local.sh
│
├── .env.example
├── .gitignore
├── turbo.json                        # Turborepo config
└── README.md
```

---

## 🔧 Core Features

### MVP (Challenge Submission)

| Feature | Priority | Status |
|---------|----------|--------|
| Story Gallery | P0 | Required |
| Multi-language Support (Hi, Ta, Bn) | P0 | Required |
| Interactive Choice System | P0 | Required |
| Multi-character Voice Acting | P0 | Required |
| Code-mixing Support | P0 | Required |
| Audio Player with Controls | P0 | Required |
| Progress Tracking | P1 | Recommended |
| Offline PWA Support | P1 | Recommended |

### Post-MVP

| Feature | Priority | Status |
|---------|----------|--------|
| User Authentication | P2 | Future |
| Voice Cloning | P2 | Future |
| Story Rating System | P2 | Future |
| Admin Dashboard | P2 | Future |
| Analytics Dashboard | P2 | Future |
| Collaborative Mode | P3 | Future |
| Mobile Apps (RN) | P3 | Future |

---

## 📊 Data Flow

### Story Playback Flow

```
User selects story
       │
       ▼
┌─────────────────────┐
│ 1. Check Cache      │
│ (Redis)             │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
 Cache Hit    Cache Miss
    │             │
    ▼             ▼
Return Audio  Check R2 Storage
              (Cloudflare)
                   │
            ┌──────┴──────┐
            │             │
         R2 Hit        R2 Miss
            │             │
            ▼             ▼
Return URL  Generate via
            Bulbul API
                 │
                 ▼
            Store in R2
            Update Redis
                 │
                 ▼
            Return Audio
```

---

## 🔐 Environment Variables

### Frontend (.env.local)

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.bhashakahani.com
NEXT_PUBLIC_WS_URL=wss://api.bhashakahani.com/ws

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_OFFLINE=true

# Sentry
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# App Config
NEXT_PUBLIC_APP_NAME=Bhasha Kahani
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/bhashakahani
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=rediss://default:pass@host:6379
REDIS_POOL_SIZE=10

# Cloudflare R2
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=bhashakahani-audio
R2_PUBLIC_URL=https://audio.bhashakahani.com

# Sarvam Bulbul
SARVAM_API_KEY=xxx
SARVAM_BASE_URL=https://api.sarvam.ai

# Sentry
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Security
SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Audio
AUDIO_CACHE_TTL_DAYS=30
MAX_AUDIO_FILE_SIZE_MB=50
```

---

## 📈 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to First Byte (TTFB) | < 200ms | Vercel Analytics |
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Audio Start Latency | < 500ms | Custom |
| API Response Time (p95) | < 200ms | Sentry |
| Cache Hit Rate | > 90% | Redis metrics |
| Offline Functionality | 100% | PWA audit |

---

## 🧪 Testing Strategy

### Frontend Testing

```
Unit Tests (Jest + React Testing Library)
├── Components
│   ├── StoryCard.test.tsx
│   ├── AudioPlayer.test.tsx
│   └── ChoiceButtons.test.tsx
├── Hooks
│   ├── useAudio.test.ts
│   └── useStory.test.ts
└── Store
    └── storyStore.test.ts

E2E Tests (Playwright)
├── story-playback.spec.ts
├── language-switch.spec.ts
├── choice-navigation.spec.ts
└── offline-mode.spec.ts
```

### Backend Testing

```
Unit Tests (pytest)
├── test_story_service.py
├── test_audio_service.py
├── test_bulbul_service.py
└── test_cache_service.py

Integration Tests
├── test_story_api.py
├── test_audio_api.py
└── test_choice_api.py

Load Tests (locust)
├── locustfile.py (1000 concurrent users)
```

---

## 🚀 Deployment Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: |
          cd apps/api && pytest
          cd ../web && npm test

  deploy-api:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: railway up --service api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-web:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| `TECH_SPEC.md` | This document - Complete technical specification |
| `ARCHITECTURE.md` | Detailed system architecture diagrams |
| `DATABASE.md` | Database schema and models |
| `API_SPEC.md` | API endpoints and request/response schemas |
| `FRONTEND.md` | Frontend component structure and state management |
| `ROADMAP.md` | Implementation timeline and milestones |
| `SETUP.md` | Local development setup guide |

---

## ✅ Success Criteria

### Challenge Submission (Feb 11)

- [ ] 3 complete stories with branching
- [ ] 3+ languages (Hindi, Tamil, Bengali)
- [ ] 5+ distinct character voices
- [ ] 2+ interactive choice points per story
- [ ] Natural code-mixing support
- [ ] < 500ms audio start latency
- [ ] Smooth 4-minute demo presentation
- [ ] PWA offline functionality

### Post-Launch

- [ ] 1000+ story plays in first month
- [ ] 80%+ story completion rate
- [ ] 40%+ repeat user rate
- [ ] 90%+ cache hit rate
- [ ] Zero critical production bugs

---

**Version:** 1.0  
**Last Updated:** February 7, 2026  
**Next Review:** Post-submission
