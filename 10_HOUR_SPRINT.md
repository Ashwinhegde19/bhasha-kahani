# 10-Hour Sprint: Bhasha Kahani

> **Goal:** Complete MVP in 10 hours  
> **Team:** Pink Panther (Backend) + Jackie Chan (Frontend)  
> **Output:** 3 stories, 3 languages, working demo

---

## ⚡ Sprint Overview

| Hour | Theme | Pink Panther | Jackie Chan | Sync |
|------|-------|--------------|-------------|------|
| 1-2 | Foundation | Setup FastAPI + DB | Setup Next.js + shadcn | End of H2 |
| 3-4 | Core Build | API endpoints + Bulbul | Components + API client | End of H4 |
| 5-6 | Integration | Audio service + caching | Player + state management | End of H6 |
| 7-8 | Features | Generate all audio | Choices + PWA + polish | End of H8 |
| 9-10 | Ship | Deploy backend | Deploy frontend | Final test |

---

## ⏱️ Hour 1-2: FOUNDATION (Setup)

### Pink Panther (Backend)

| Time | Task | Output |
|------|------|--------|
| 0:00-0:30 | Initialize FastAPI project, venv, install deps | `apps/api/` running |
| 0:30-1:00 | Setup SQLAlchemy models (User, Story, Node, Choice) | Models defined |
| 1:00-1:30 | Setup Alembic, create migration, run it | DB tables created |
| 1:30-2:00 | Create Bulbul service, test API connection | Audio generation works |

**Commands:**
```bash
cd apps/api
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic httpx python-dotenv
alembic init alembic
# Create models
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

### Jackie Chan (Frontend)

| Time | Task | Output |
|------|------|--------|
| 0:00-0:30 | Initialize Next.js 15 with TypeScript + Tailwind | `apps/web/` running |
| 0:30-1:00 | Initialize shadcn/ui, install components | shadcn working |
| 1:00-1:30 | Install deps (Zustand, TanStack Query, Howler.js) | All deps installed |
| 1:30-2:00 | Create folder structure, base layout | Project organized |

**Commands:**
```bash
cd apps/web
npx create-next-app@latest . --typescript --tailwind --app
npx shadcn@latest init
npx shadcn add button card slider avatar badge dialog
npm install zustand @tanstack/react-query @tanstack/react-query-devtools howler axios
npm install -D @types/howler
```

---

### 🔄 SYNC POINT: End of Hour 2 (15 min)

**Discuss:**
- [ ] API response format for stories
- [ ] Shared TypeScript types
- [ ] Environment variables

**Agree on:**
```typescript
// Story type
interface Story {
  id: string;
  slug: string;
  title: string;
  description: string;
  language: 'hi' | 'ta' | 'bn';
  coverImage: string;
  durationMin: number;
  nodes: StoryNode[];
}

// API base URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ⏱️ Hour 3-4: CORE BUILD

### Pink Panther (Backend)

| Time | Task | Output |
|------|------|--------|
| 2:00-2:30 | `POST /auth/anonymous` - JWT token | Auth works |
| 2:30-3:00 | `GET /stories` - list all stories | Stories endpoint |
| 3:00-3:30 | `GET /stories/{slug}` - story detail | Story with nodes |
| 3:30-4:00 | `POST /stories/{slug}/choices` - make choice | Choice endpoint |

**Quick Test:**
```bash
curl http://localhost:8000/stories
curl http://localhost:8000/stories/clever-crow
```

---

### Jackie Chan (Frontend)

| Time | Task | Output |
|------|------|--------|
| 2:00-2:30 | Setup API client (axios), TanStack Query | API layer ready |
| 2:30-3:00 | Create StoryCard component | Card displays story |
| 3:00-3:30 | Create StoryGrid, /stories page | Gallery page works |
| 3:30-4:00 | Create Zustand stores (user, story, audio) | State management ready |

**Test:** Navigate to `/stories`, see stories loading

---

### 🔄 SYNC POINT: End of Hour 4 (15 min)

**Test Together:**
- [ ] Frontend calls backend API successfully
- [ ] Stories display in gallery
- [ ] CORS configured properly

**Fix any CORS/auth issues NOW**

---

## ⏱️ Hour 5-6: INTEGRATION

### Pink Panther (Backend)

| Time | Task | Output |
|------|------|--------|
| 4:00-4:30 | `GET /audio/{node_id}` - audio URL endpoint | Audio endpoint |
| 4:30-5:00 | Setup Redis caching for audio metadata | Cache working |
| 5:00-5:30 | Implement audio generation pipeline | Generate audio on-demand |
| 5:30-6:00 | Generate audio for 1 story (Hindi) | 5-10 audio files ready |

---

### Jackie Chan (Frontend)

| Time | Task | Output |
|------|------|--------|
| 4:00-4:30 | Create AudioPlayer component with Howler.js | Player renders |
| 4:30-5:00 | Implement play/pause/seek/volume | Controls work |
| 5:00-5:30 | Create /play/[storyId] page | Story player page |
| 5:30-6:00 | Connect player to API, test playback | Audio plays end-to-end |

---

### 🔄 SYNC POINT: End of Hour 6 (20 min)

**Demo Together:**
- [ ] Click story → Opens player
- [ ] Audio plays
- [ ] Can pause/play
- [ ] No errors in console

**Critical:** Audio MUST be playing by end of this hour.

---

## ⏱️ Hour 7-8: FEATURES + POLISH

### Pink Panther (Backend)

| Time | Task | Output |
|------|------|--------|
| 6:00-6:45 | Write story data for all 3 stories | 3 JSON files |
| 6:45-7:30 | Bulk generate audio (all stories, all languages) | All audio files |
| 7:30-8:00 | Progress tracking endpoints | Save/restore progress |

**Stories to Write:**
1. **The Clever Crow** (Pan-Indian)
2. **The Kind Woodcutter** (Bengali)
3. **Tenali Raman** (Tamil)

---

### Jackie Chan (Frontend)

| Time | Task | Output |
|------|------|--------|
| 6:00-6:45 | Create ChoiceOverlay component | Choices display |
| 6:45-7:30 | Implement choice selection + branch navigation | Choices work |
| 7:30-8:00 | Add LanguageSelector + code-mix slider | Language switch works |

---

### 🔄 SYNC POINT: End of Hour 8 (20 min)

**Full Integration Test:**
- [ ] Play story → Choice appears → Select → Branch plays
- [ ] Switch language → Audio in new language
- [ ] 3 stories playable
- [ ] All choice branches work

**Bug fix session - squash all issues**

---

## ⏱️ Hour 9-10: SHIP IT

### Pink Panther (Backend Deployment)

| Time | Task | Output |
|------|------|--------|
| 8:00-8:30 | Upload all audio to Cloudflare R2 | CDN ready |
| 8:30-9:00 | Deploy to Railway | Backend live |
| 9:00-9:30 | Configure prod DB, run migrations | DB ready |
| 9:30-10:00 | Final API tests on production | Production API works |

**Deploy Commands:**
```bash
railway login
railway link
railway up
railway domain  # Get production URL
```

---

### Jackie Chan (Frontend Deployment)

| Time | Task | Output |
|------|------|--------|
| 8:00-8:30 | Add PWA manifest + service worker | PWA installable |
| 8:30-9:00 | Mobile responsive pass | Works on mobile |
| 9:00-9:30 | Deploy to Vercel | Frontend live |
| 9:30-10:00 | Configure prod API URL, final tests | Production works |

**Deploy Commands:**
```bash
vercel --prod
# Update NEXT_PUBLIC_API_URL to Railway URL
```

---

### 🎯 FINAL TEST (Last 30 min - Both)

**Complete Walkthrough:**
1. [ ] Open production URL on phone
2. [ ] Install PWA
3. [ ] Play "The Clever Crow" in Hindi
4. [ ] Make a choice
5. [ ] Switch to Tamil
6. [ ] Play "Tenali Raman"
7. [ ] Turn off wifi - does it still work?

**If all pass = SHIP IT** 🚀

---

## 📋 Pre-Sprint Checklist

Before starting the 10-hour sprint:

- [ ] Both have GitHub access
- [ ] Both have Railway account
- [ ] Both have Vercel account
- [ ] Pink Panther: Sarvam API key ready
- [ ] Pink Panther: Cloudflare R2 credentials
- [ ] Jackie Chan: Node.js 18+ installed
- [ ] Pink Panther: Python 3.9+ installed
- [ ] Both: Read CONFLICT_FREE_WORKFLOW.md
- [ ] Communication channel ready (Discord/Slack)
- [ ] Standby for 10 hours (no interruptions!)

---

## ⚡ Emergency Shortcuts (If Running Late)

### Hour 5 - Audio Not Working?
**Quick fix:** Use pre-generated MP3s, skip dynamic generation

### Hour 7 - Only 1 Story Ready?
**Ship with 1 polished story, add others post-demo**

### Hour 9 - Deploy Failing?
**Use Railway + Vercel auto-deploy from GitHub**

---

## ✅ Success Criteria (All Must Pass)

### Technical
- [ ] 1 complete story with branching (minimum)
- [ ] 3 languages working (Hindi, Tamil, Bengali)
- [ ] 2+ choice points per story
- [ ] Audio < 1 second start time
- [ ] Offline PWA working

### Demo
- [ ] 4-minute presentation
- [ ] Smooth story flow
- [ ] No technical glitches
- [ ] Live production URL

---

## 💪 Team Spirit

**Pink Panther:** "Backend will be rock solid"  
**Jackie Chan:** "Frontend will be smooth as silk"  

**Together:** Ship in 10 hours! 🚀

---

**Start the timer. Let's go!** ⏱️
