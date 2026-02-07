# Bhasha Kahani - Team Collaboration Guide

> **Project:** Bhasha Kahani - Multilingual Interactive Folktale Platform  
> **Deadline:** February 11, 2026 (4 days)  
> **Team Size:** 2 people  
> **Last Updated:** February 7, 2026

---

## 🚨 READ THIS FIRST: Conflict-Free Workflow

**To avoid merge conflicts and issues, follow this exactly:**

### Morning (Before You Start Working)
```bash
git checkout develop && git pull
git checkout feature/your-branch
git rebase develop
```

### During Day (Every 30-60 minutes)
```bash
git add . && git commit -m "[PP] feat: what you did"
```

### Evening (Before You Stop)
```bash
git push origin feature/your-branch
# Create PR on GitHub, request review, DON'T merge yourself
```

**📖 Full details:** See `CONFLICT_FREE_WORKFLOW.md`

---

## 👥 Team Roles

### **Pink Panther - Backend Lead** 
**Focus:** API, Database, Audio Generation, Infrastructure

**You Own:**
- `apps/api/` - Entire FastAPI backend
- `packages/shared/` - Shared types (coordinate with Jackie Chan)
- `scripts/` - Audio generation, seeding scripts
- `infra/` - Infrastructure configuration
- Railway deployment

**Your Stack:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Cloudflare R2

---

### **Jackie Chan - Frontend Lead**
**Focus:** UI, Audio Player, User Experience, PWA

**You Own:**
- `apps/web/` - Entire Next.js frontend
- `packages/shared/` - Shared types (coordinate with Pink Panther)
- UI components, animations, responsive design
- Vercel deployment

**Your Stack:** Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Zustand, Howler.js

---

## 🌿 Git Workflow

### Branch Structure

```
main (production - protected, requires PR)
  │
  └── develop (integration - protected, requires PR)
        │
        ├── feature/PP-api-setup           # Pink Panther's branches
        ├── feature/PP-db-models
        ├── feature/PP-bulbul-int
        ├── feature/PP-day2-audio
        ├── feature/PP-day3-cache
        │
        ├── feature/JC-nextjs-setup        # Jackie Chan's branches
        ├── feature/JC-ui-components
        ├── feature/JC-audio-player
        ├── feature/JC-day2-storyplayer
        ├── feature/JC-day3-choices
```

### Naming Convention

- **Pink Panther:** `feature/PP-<day>-<description>`
- **Jackie Chan:** `feature/JC-<day>-<description>`

**Examples:**
- `feature/PP-day1-models`
- `feature/JC-day1-setup`
- `feature/PP-day2-bulbul`
- `feature/JC-day2-player`

### Daily Git Workflow

```bash
# ===== MORNING SYNC =====
# 1. Switch to develop and pull latest
git checkout develop
git pull origin develop

# 2. Update your feature branch
git checkout feature/your-branch
git rebase develop

# ===== WORK =====
# Make small, frequent commits

# ===== EVENING PUSH =====
# 3. Push your branch
git push origin feature/your-branch

# 4. Create PR to develop (not main!)
# 5. Request review from teammate
```

### Commit Message Format

```
[PP] feat: implement GET /stories endpoint
[JC] feat: add AudioPlayer component with Howler.js
[PP] fix: handle missing audio files in R2
[JC] style: improve mobile responsiveness
```

- `[PP]` = Pink Panther, `[JC]` = Jackie Chan
- `feat:` = new feature
- `fix:` = bug fix
- `style:` = UI/styling changes
- `docs:` = documentation
- `refactor:` = code refactoring

---

## 📋 Daily Tasks

### **Day 1: Foundation (February 7)**

#### Pink Panther Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| A1.1 | Initialize FastAPI project structure | P0 | 30m | ⬜ |
| A1.2 | Setup PostgreSQL connection with SQLAlchemy | P0 | 30m | ⬜ |
| A1.3 | Create database models (User, Story, Character) | P0 | 45m | ⬜ |
| A1.4 | Setup Alembic migrations | P0 | 15m | ⬜ |
| A1.5 | **API CONTRACT DISCUSSION** with Jackie Chan | P0 | 30m | ⬜ |
| A1.6 | Implement `POST /auth/anonymous` endpoint | P0 | 30m | ⬜ |
| A1.7 | Implement `GET /stories` endpoint | P0 | 30m | ⬜ |
| A1.8 | Create Bulbul API service module | P1 | 45m | ⬜ |
| A1.9 | Test Bulbul API with sample text | P1 | 15m | ⬜ |
| A1.10 | Write "The Clever Crow" story data (JSON) | P1 | 45m | ⬜ |

#### Jackie Chan Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| B1.1 | Initialize Next.js 15 project with TypeScript | P0 | 30m | ⬜ |
| B1.2 | Setup Tailwind CSS configuration | P0 | 15m | ⬜ |
| B1.3 | Initialize shadcn/ui | P0 | 15m | ⬜ |
| B1.4 | Install dependencies (Zustand, TanStack Query, Howler.js) | P0 | 15m | ⬜ |
| B1.5 | Create folder structure (app, components, hooks, store) | P0 | 15m | ⬜ |
| B1.6 | **API CONTRACT DISCUSSION** with Pink Panther | P0 | 30m | ⬜ |
| B1.7 | Setup Zustand stores (user, audio, story) | P0 | 30m | ⬜ |
| B1.8 | Setup TanStack Query client | P0 | 15m | ⬜ |
| B1.9 | Create LanguageSelector component | P0 | 30m | ⬜ |
| B1.10 | Create StoryCard component | P0 | 30m | ⬜ |
| B1.11 | Create basic layout (Navbar, Footer) | P0 | 30m | ⬜ |

#### Day 1 Sync Point (2:00 PM)

**Agenda (30 minutes):**
1. Review API response formats together
2. Agree on shared TypeScript types
3. Define Story, Character, Node interfaces
4. Confirm endpoint paths

**Deliverables:**
- ✅ API contracts documented in `API_SPEC.md`
- ✅ Shared types in `packages/shared/src/types/`

---

### **Day 2: Core Features (February 8)**

#### Pink Panther Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| A2.1 | Implement `GET /stories/{slug}` endpoint | P0 | 30m | ⬜ |
| A2.2 | Implement `GET /stories/{slug}/nodes/{id}` endpoint | P0 | 30m | ⬜ |
| A2.3 | Implement choice logic endpoints | P0 | 45m | ⬜ |
| A2.4 | Create `POST /stories/{slug}/choices` endpoint | P0 | 30m | ⬜ |
| A2.5 | Implement `GET /audio/{node_id}` endpoint | P0 | 45m | ⬜ |
| A2.6 | Setup R2 storage integration | P0 | 30m | ⬜ |
| A2.7 | Generate test audio for 1 story (Hindi) | P0 | 30m | ⬜ |
| A2.8 | Write "The Kind Woodcutter" story (Bengali) | P1 | 30m | ⬜ |
| A2.9 | Write "Tenali Raman" story (Tamil) | P1 | 30m | ⬜ |

#### Jackie Chan Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| B2.1 | Build Story Gallery page (`/stories`) | P0 | 45m | ⬜ |
| B2.2 | Build Story Detail page (`/stories/[slug]`) | P0 | 45m | ⬜ |
| B2.3 | Create StoryGrid component | P0 | 30m | ⬜ |
| B2.4 | Integrate TanStack Query for data fetching | P0 | 30m | ⬜ |
| B2.5 | Build AudioPlayer component skeleton | P0 | 30m | ⬜ |
| B2.6 | Integrate Howler.js for audio playback | P0 | 45m | ⬜ |
| B2.7 | Implement play/pause/seek controls | P0 | 30m | ⬜ |
| B2.8 | Add volume control | P1 | 15m | ⬜ |
| B2.9 | Build Story Player page (`/play/[storyId]`) | P0 | 45m | ⬜ |

#### Day 2 Sync Point (4:00 PM)

**Agenda (1 hour):**
1. Test API integration together
2. Verify audio playback works end-to-end
3. Debug any CORS/audio issues
4. Adjust timelines if needed

**Deliverables:**
- ✅ One complete story playable from start to finish
- ✅ Audio plays correctly in browser

---

### **Day 3: Integration & Polish (February 9)**

#### Pink Panther Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| A3.1 | Implement progress tracking API | P0 | 45m | ⬜ |
| A3.2 | Create `GET /users/progress` endpoint | P0 | 30m | ⬜ |
| A3.3 | Create `POST /users/progress` endpoint | P0 | 30m | ⬜ |
| A3.4 | Setup Upstash Redis connection | P0 | 30m | ⬜ |
| A3.5 | Implement audio metadata caching | P0 | 30m | ⬜ |
| A3.6 | Bulk generate audio for all stories | P0 | 2h | ⬜ |
| A3.7 | Upload all audio files to R2 | P0 | 30m | ⬜ |
| A3.8 | Create analytics events endpoint | P1 | 30m | ⬜ |
| A3.9 | Setup Sentry error tracking (backend) | P1 | 15m | ⬜ |

#### Jackie Chan Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| B3.1 | Create ChoiceOverlay component | P0 | 45m | ⬜ |
| B3.2 | Create ChoiceButton component | P0 | 30m | ⬜ |
| B3.3 | Implement choice selection flow | P0 | 45m | ⬜ |
| B3.4 | Build progress state management | P0 | 30m | ⬜ |
| B3.5 | Implement language switcher | P0 | 30m | ⬜ |
| B3.6 | Add code-mixing slider | P0 | 30m | ⬜ |
| B3.7 | Create PWA manifest | P0 | 15m | ⬜ |
| B3.8 | Add service worker for offline support | P0 | 45m | ⬜ |
| B3.9 | Mobile responsiveness pass | P0 | 45m | ⬜ |
| B3.10 | Add loading states and error boundaries | P1 | 30m | ⬜ |
| B3.11 | Setup Sentry error tracking (frontend) | P1 | 15m | ⬜ |

#### Day 3 Sync Point (6:00 PM)

**Agenda (1 hour):**
1. Full end-to-end testing
2. Test all choice branches
3. Test language switching
4. Test offline mode
5. Bug fix session

**Deliverables:**
- ✅ All 3 stories playable
- ✅ All languages working
- ✅ PWA installable
- ✅ Offline mode functional

---

### **Day 4: Deployment & Demo Prep (February 10)**

#### Pink Panther Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| A4.1 | Deploy backend to Railway | P0 | 30m | ⬜ |
| A4.2 | Configure production environment variables | P0 | 15m | ⬜ |
| A4.3 | Setup Railway database | P0 | 15m | ⬜ |
| A4.4 | Run migrations on production DB | P0 | 10m | ⬜ |
| A4.5 | Seed production database | P0 | 10m | ⬜ |
| A4.6 | Load testing with locust | P1 | 30m | ⬜ |
| A4.7 | API documentation review | P1 | 15m | ⬜ |

#### Jackie Chan Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| B4.1 | Deploy frontend to Vercel | P0 | 15m | ⬜ |
| B4.2 | Configure production API URL | P0 | 10m | ⬜ |
| B4.3 | Cross-browser testing | P0 | 30m | ⬜ |
| B4.4 | Mobile device testing | P0 | 30m | ⬜ |
| B4.5 | Performance optimization | P1 | 30m | ⬜ |
| B4.6 | SEO meta tags | P1 | 15m | ⬜ |
| B4.7 | Favicon and icons | P1 | 15m | ⬜ |

#### Joint Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| J4.1 | Write demo script | P0 | 30m | ⬜ |
| J4.2 | Practice demo (5+ times) | P0 | 1h | ⬜ |
| J4.3 | End-to-end testing | P0 | 1h | ⬜ |
| J4.4 | Record backup demo video | P1 | 30m | ⬜ |
| J4.5 | Update README.md | P1 | 30m | ⬜ |
| J4.6 | Final bug fixes | P0 | 1h | ⬜ |

---

### **Day 5: Submission Day (February 11)**

| # | Task | Owner | Status |
|---|------|-------|--------|
| S1 | Final demo run-through | Both | ⬜ |
| S2 | Deploy any last fixes | A/B as needed | ⬜ |
| S3 | Push final code to GitHub | Both | ⬜ |
| S4 | Create release tag | Pink Panther or Jackie Chan | ⬜ |
| S5 | Submit project | Both | ⬜ |
| S6 | Post on social media (#TheMicIsYours) | Both | ⬜ |
| S7 | Email confirmation | Both | ⬜ |

---

## 🔒 Conflict Prevention Rules

### File Ownership (NEVER touch teammate's files)

```yaml
# Pink Panther owns (DO NOT TOUCH if you're Jackie Chan):
apps/api/**
scripts/**
infra/terraform/**

# Jackie Chan owns (DO NOT TOUCH if you're Pink Panther):
apps/web/**
# Except: apps/web/.env.local (your own)

# SHARED (discuss before changing):
packages/shared/**
API_SPEC.md
DATABASE.md
turbo.json
.github/workflows/
```

### API-First Development

Before coding any feature that needs backend:

1. **Pink Panther** updates `API_SPEC.md` with endpoint details
2. **Jackie Chan** reviews and approves
3. Both implement simultaneously
4. Test together at sync point

### Shared Types Package

```
packages/shared/
├── src/
│   ├── types/
│   │   ├── story.ts       # Story, StoryNode, Character
│   │   ├── api.ts         # API request/response types
│   │   ├── user.ts        # User, UserProgress
│   │   └── audio.ts       # AudioFile, AudioState
│   └── constants/
│       ├── languages.ts   # Language codes, configs
│       └── voices.ts      # Bulbul voice mappings
└── package.json
```

**To use in frontend:**
```typescript
import { Story, StoryNode } from '@bhasha/shared';
```

**To use in backend:**
```python
from bhasha_shared.types import Story, StoryNode
```

---

## 📞 Communication Protocol

### Daily Standup (15 min at agreed time)

```
Pink Panther: Yesterday I completed X, today I'm working on Y, 
          blockers: Z

Jackie Chan: Yesterday I completed P, today I'm working on Q,
          blockers: R

Both: Sync on any API changes needed
```

### Emergency Communication

- **Slack/Discord** for quick questions (< 5 min response)
- **Video call** for complex issues (> 15 min discussion)
- **GitHub comment** on PRs for code-specific feedback

### Response Time Expectations

| Priority | Response Time |
|----------|--------------|
| Blocker (can't proceed) | < 30 minutes |
| Question (can workaround) | < 2 hours |
| Review request | < 4 hours |
| General discussion | < 24 hours |

---

## 🧪 Testing Checklist

### Before Each PR

- [ ] Code runs without errors
- [ ] No console warnings
- [ ] Mobile responsive (if UI)
- [ ] API returns expected format (if backend)

### Day 3 Integration Test

- [ ] Story loads from API
- [ ] Audio plays within 500ms
- [ ] Choices display correctly
- [ ] Branch navigation works
- [ ] Progress saves correctly
- [ ] Language switching works
- [ ] Offline mode works (PWA)

### Day 4 Final Test

- [ ] All 3 stories playable
- [ ] All languages working (Hi, Ta, Bn)
- [ ] All code-mix ratios working
- [ ] Mobile experience smooth
- [ ] Production deployment live

---

## 🚨 Risk Mitigation

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Bulbul API down | Pre-generate all audio by Day 3 | A |
| Deployment failure | Test deploy on Day 3 evening | Pink Panther & Jackie Chan |
| API contract mismatch | Daily sync + shared types | Both |
| Merge conflicts | Clear file ownership rules | Both |
| Feature creep | Strict MVP scope enforcement | Both |
| Demo failure | Record backup video | B |

---

## ✅ Pre-Start Checklist

Before starting Day 1, ensure:

- [ ] Both have GitHub access to repo
- [ ] Both have same Node.js (18+) installed
- [ ] Both have same Python (3.9+) installed
- [ ] Agreed on code formatter (Prettier/Black)
- [ ] Pre-commit hooks installed
- [ ] Branch protection rules configured
- [ ] Daily standup time scheduled
- [ ] Communication channels setup (Slack/Discord)
- [ ] Both have access to:
  - [ ] Railway account
  - [ ] Vercel account
  - [ ] Cloudflare R2
  - [ ] Upstash Redis
  - [ ] Sarvam AI API key

---

## 📝 Task Status Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Complete |
| ⏸️ | Blocked |

---

## 🎯 Success Criteria

### Technical (Must Have)
- [ ] 3 complete stories with branching
- [ ] 3+ languages (Hindi, Tamil, Bengali)
- [ ] 5+ distinct character voices
- [ ] 2+ interactive choice points per story
- [ ] Natural code-mixing support
- [ ] < 500ms audio start time
- [ ] Offline PWA working

### Demo (Must Have)
- [ ] 4-minute presentation
- [ ] Smooth transitions
- [ ] No technical glitches
- [ ] Emotional hook
- [ ] Clear value proposition

### Submission (Must Have)
- [ ] GitHub repo public
- [ ] Live demo URL
- [ ] Demo video (backup)
- [ ] Social media post with #TheMicIsYours

---

**Questions?** Discuss in your team channel or during standup.

**Let's build something amazing! 🚀**
