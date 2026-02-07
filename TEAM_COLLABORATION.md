# Bhasha Kahani - Team Collaboration Guide

> **Project:** Bhasha Kahani - Multilingual Interactive Folktale Platform  
> **Deadline:** February 11, 2026 (4 days)  
> **Team Size:** 2 people  
> **Last Updated:** February 7, 2026

---

## 🚨 READ THIS FIRST: 10-Hour Sprint Mode

> **This project is now a 10-HOUR SPRINT**  
> **Read:** `10_HOUR_SPRINT.md` for complete hour-by-hour plan

### The Sprint Structure

| Hours | Phase | Pink Panther | Jackie Chan |
|-------|-------|--------------|-------------|
| 1-2 | Foundation | Setup FastAPI + DB | Setup Next.js |
| 3-4 | Core Build | API endpoints | UI components |
| 5-6 | Integration | Audio service | Audio player |
| 7-8 | Features | Generate all audio | Choices + PWA |
| 9-10 | Ship | Deploy backend | Deploy frontend |

### Quick Git (No Conflicts)
```bash
# Every 1-2 hours
git add . && git commit -m "[PP] feat: what you did"
git push origin feature/PP-sprint  # or feature/JC-sprint

# To share with teammate
git checkout develop
git merge feature/PP-sprint
git push origin develop
```

### Sync Points (5 times in 10 hours)
- Hour 2: API contracts
- Hour 4: Integration test
- Hour 6: Audio playback
- Hour 8: Full story test
- Hour 10: Production test

**📖 Full workflow:** See `CONFLICT_FREE_WORKFLOW.md`  
**📖 Hour plan:** See `10_HOUR_SPRINT.md`

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

## 📋 10-Hour Sprint Tasks

### **Hour 1-2: Foundation (Setup)**

| Time | Pink Panther | Jackie Chan | Status |
|------|--------------|-------------|--------|
| 0:00-0:30 | Initialize FastAPI, install deps | Initialize Next.js, Tailwind | ⬜ |
| 0:30-1:00 | Create SQLAlchemy models | Setup shadcn/ui components | ⬜ |
| 1:00-1:30 | Setup Alembic, run migrations | Install Zustand, TanStack Query, Howler | ⬜ |
| 1:30-2:00 | Test Bulbul API connection | Create folder structure | ⬜ |

**🔄 SYNC (15 min):** Agree on API contracts, shared types

**Deliverables:**
- Backend runs on localhost:8000
- Frontend runs on localhost:3000
- Shared types agreed

---

### **Hour 3-4: Core Build**

#### Pink Panther Tasks

| # | Task | Priority | Time | Status |
|---|------|----------|------|--------|
| A2.1 | Implement `GET /stories/{slug}` endpoint | P0 | 30m | ⬜ |
| A2.2 | Implement `GET /stories/{slug}/nodes/{id}` endpoint | P0 | 30m | ⬜ |
| A2.3 | Implement choice logic endpoints | P0 | 45m | ⬜ |
| A2.4 | Create `POST /stories/{slug}/choices` endpoint | P0 | 30m | ⬜ |
| A2.5 | Implement `GET /audio/{node_id}` endpoint | P0 | 45m | ⬜ |
| A2.6 | Setup R2 storage integration | P0 | 30m | ⬜ |
| A2.7 | Generate test audio for 1 story (Hindi, English, Kannada) | P0 | 30m | ⬜ |
| Time | Pink Panther | Jackie Chan | Status |
|------|--------------|-------------|--------|
| 2:00-2:30 | `POST /auth/anonymous` | Setup API client, TanStack Query | ⬜ |
| 2:30-3:00 | `GET /stories` endpoint | Create StoryCard component | ⬜ |
| 3:00-3:30 | `GET /stories/{slug}` endpoint | Create StoryGrid, /stories page | ⬜ |
| 3:30-4:00 | `POST /stories/{slug}/choices` | Create Zustand stores | ⬜ |

**🔄 SYNC (15 min):** Test API integration, fix CORS

**Deliverables:**
- API endpoints respond correctly
- Frontend displays stories
- CORS configured

---

### **Hour 5-6: Integration (Audio)**

| Time | Pink Panther | Jackie Chan | Status |
|------|--------------|-------------|--------|
| 4:00-4:30 | `GET /audio/{node_id}` endpoint | Create AudioPlayer component | ⬜ |
| 4:30-5:00 | Setup Redis caching | Implement Howler.js integration | ⬜ |
| 5:00-5:30 | Audio generation pipeline | Create /play/[storyId] page | ⬜ |
| 5:30-6:00 | Generate 1 story audio (Hindi, English, Kannada) | Connect player to API | ⬜ |

**🔄 SYNC (20 min):** Audio MUST play end-to-end

**Deliverables:**
- Audio endpoint works
- Player displays and plays
- No console errors

---

### **Hour 7-8: Features (Stories + Choices)**

| Time | Pink Panther | Jackie Chan | Status |
|------|--------------|-------------|--------|
| 6:00-6:45 | Write 3 stories (JSON) | Create ChoiceOverlay component | ⬜ |
| 6:45-7:30 | Bulk generate all audio | Implement choice navigation | ⬜ |
| 7:30-8:00 | Progress endpoints | LanguageSelector + code-mix slider | ⬜ |

**🔄 SYNC (20 min):** Full story test, all choices work

**Deliverables:**
- 3 stories in database
- Choices display and navigate
- All audio generated

---

### **Hour 9-10: Ship (Deploy)**

| Time | Pink Panther | Jackie Chan | Status |
|------|--------------|-------------|--------|
| 8:00-8:30 | Upload audio to R2 | Add PWA manifest + service worker | ⬜ |
| 8:30-9:00 | Deploy to Railway | Mobile responsive pass | ⬜ |
| 9:00-9:30 | Test production API | Deploy to Vercel | ⬜ |
| 9:30-10:00 | Final backend tests | Test production, final fixes | ⬜ |

**🎯 FINAL TEST (Both):**
- [ ] Production URL works on phone
- [ ] PWA installs
- [ ] Story plays end-to-end
- [ ] Choices work
- [ ] Offline mode works

---

## ⚡ Sprint Tips

### Communication During Sprint
- **Keep voice/video call open** entire 10 hours
- **Quick questions:** < 2 min response
- **Blockers:** Immediate help
- **Sync points:** Non-negotiable, stop work and sync

### If Falling Behind
- Skip non-essential: analytics, Sentry, tests
- Focus on 1 perfect story vs 3 mediocre
- Deploy early, test continuously

### Quality Gates (Must Pass)
- Audio plays < 1 second
- No console errors
- Mobile responsive
- Deployed and working

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

### Before Each Commit (during sprint)

- [ ] Code runs without errors
- [ ] No console warnings
- [ ] Mobile responsive (if UI)
- [ ] API returns expected format (if backend)

### Hour 6 Test (Audio Integration)

- [ ] Story loads from API
- [ ] Audio plays within 1 second
- [ ] Player controls work
- [ ] No console errors

### Hour 8 Test (Full Features)

- [ ] All 3 stories playable
- [ ] Choices display correctly
- [ ] Branch navigation works
- [ ] Language switching works
- [ ] Offline mode works (PWA)

### Hour 10 Final Test

- [ ] Production URL live
- [ ] All languages working (Hi, Ta, Bn)
- [ ] Mobile experience smooth
- [ ] PWA installable
- [ ] Demo ready

---

## 🚨 Risk Mitigation

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Bulbul API down | Pre-generate all audio by Hour 7 | Pink Panther |
| Deployment failure | Deploy by Hour 9, test early | Pink Panther & Jackie Chan |
| API contract mismatch | Sync at Hour 2 + shared types | Both |
| Merge conflicts | Clear file ownership + frequent commits | Both |
| Feature creep | Strict MVP scope, skip non-essential | Both |
| Demo failure | Test continuously, fix early | Both |

---

## ✅ Pre-Start Checklist

Before starting the 10-hour sprint, ensure:

- [ ] Both have GitHub access to repo
- [ ] Both have same Node.js (18+) installed
- [ ] Both have same Python (3.9+) installed
- [ ] Agreed on code formatter (Prettier/Black)
- [ ] Pre-commit hooks installed
- [ ] Branch protection rules configured
- [ ] 10-hour block cleared (no interruptions)
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
- [ ] 3+ languages (English, Hindi, Kannada)
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
