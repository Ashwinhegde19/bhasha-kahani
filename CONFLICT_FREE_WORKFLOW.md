# Conflict-Free Collaboration Workflow

> **For:** Pink Panther (Backend) & Jackie Chan (Frontend)  
> **Goal:** Zero merge conflicts, smooth remote collaboration  
> **Last Updated:** February 7, 2026

---

## 🎯 The Golden Rule

> **"NEVER work on the same file at the same time"**

If you follow this rule + the workflow below, you'll have **zero conflicts**.

---

## 🌅 Daily Workflow (Step-by-Step)

### ☀️ Morning Routine (Do This First!)

```bash
# STEP 1: Save your current work
git status                    # See what you've changed
git add .                     # Stage your changes
git commit -m "[PP] wip: saving morning progress"  # or [JC]

# STEP 2: Get latest from teammate
git checkout develop
git pull origin develop       # Get teammate's overnight work

# STEP 3: Update your branch
git checkout feature/your-branch
git rebase develop            # Put your work ON TOP of latest develop

# STEP 4: Handle any issues (rare)
# If rebase has conflicts, see "Emergency: Fixing Conflicts" below
```

**Why this works:** You're always building on top of the latest code, never behind.

---

## 📝 During The Day

### Commit Frequently (Every 30-60 minutes)

```bash
# Small commits are easier to merge
git add .
git commit -m "[PP] feat: add User model"

# ... later ...
git add .
git commit -m "[PP] feat: add Story model"

# ... later ...
git add .
git commit -m "[PP] feat: setup database connection"
```

**Benefit:** If there's an issue, you can undo just the last small change, not a whole day's work.

---

## 🌙 Evening Routine (Before You Stop Working)

```bash
# STEP 1: Commit everything
git add .
git commit -m "[PP] feat: day 1 progress - database models complete"

# STEP 2: Push your branch
git push origin feature/PP-api-setup

# STEP 3: Create Pull Request on GitHub
# - Go to GitHub repo
# - Click "Compare & pull request"
# - Base: develop ← Compare: feature/PP-api-setup
# - Add title: "[PP] Day 1: Database models and API setup"
# - Tag Jackie Chan as reviewer
# - Click "Create Pull Request"

# STEP 4: DO NOT MERGE YOURSELF
# Wait for teammate to review and approve
```

---

## 🔄 The Complete Day Example

### Pink Panther's Day (Backend)

```bash
# 9:00 AM - Morning sync
git checkout develop && git pull
git checkout feature/PP-api-setup
git rebase develop

# 9:30 AM - Work on User model
git add . && git commit -m "[PP] feat: add User model"

# 10:30 AM - Work on Story model  
git add . && git commit -m "[PP] feat: add Story model"

# 12:00 PM - Quick sync (optional)
git checkout develop && git pull  # See if Jackie pushed anything
git checkout feature/PP-api-setup
git rebase develop

# 2:00 PM - Sync meeting with Jackie Chan
# Discuss API contracts

# 3:00 PM - Work on API endpoints
git add . && git commit -m "[PP] feat: add GET /stories endpoint"

# 6:00 PM - End of day
git add . && git commit -m "[PP] feat: day 1 complete - models and endpoints"
git push origin feature/PP-api-setup
# Create PR on GitHub
```

### Jackie Chan's Day (Frontend)

```bash
# 9:00 AM - Morning sync
git checkout develop && git pull
git checkout feature/JC-nextjs-setup
git rebase develop

# 9:30 AM - Setup Next.js
git add . && git commit -m "[JC] feat: initialize Next.js project"

# 10:30 AM - Setup shadcn/ui
git add . && git commit -m "[JC] feat: setup shadcn/ui components"

# 12:00 PM - Quick sync (optional)
git checkout develop && git pull  # See if Pink Panther pushed anything
git checkout feature/JC-nextjs-setup
git rebase develop

# 2:00 PM - Sync meeting with Pink Panther
# Discuss API contracts

# 3:00 PM - Create components
git add . && git commit -m "[JC] feat: add StoryCard component"

# 6:00 PM - End of day
git add . && git commit -m "[JC] feat: day 1 complete - project setup and components"
git push origin feature/JC-nextjs-setup
# Create PR on GitHub
```

---

## ✅ The Review & Merge Process

### When You Wake Up (Next Morning)

```bash
# Check if your PR was approved and merged
git checkout develop
git pull origin develop

# If your PR is merged, delete old branch
git branch -d feature/PP-api-setup  # or feature/JC-nextjs-setup

# Create new branch for today
git checkout -b feature/PP-day2-audio-service
```

### Reviewing Teammate's PR

```bash
# 1. Check out their branch locally
git fetch origin
git checkout feature/JC-nextjs-setup  # Jackie's branch

# 2. Test it works
# - For backend: run tests, check API
# - For frontend: run dev server, check UI

# 3. If good, approve on GitHub
# Click "Files changed" → "Review changes" → "Approve"

# 4. Merge if approved
# Click "Merge pull request" → "Squash and merge"

# 5. Update your local develop
git checkout develop
git pull origin develop
```

---

## 🚨 Emergency: Fixing Conflicts

### If You Get a Conflict During Rebase

```bash
git checkout feature/PP-api-setup
git rebase develop

# CONFLICT! You'll see:
# Auto-merging apps/api/models/story.py
# CONFLICT (content): Merge conflict in apps/api/models/story.py

# STEP 1: See which files have conflicts
git status

# STEP 2: Open each conflicted file, look for:
<<<<<<< HEAD
# (teammate's code)
=======
# (your code)
>>>>>>> feature/PP-api-setup

# STEP 3: Keep BOTH code sections (they're probably different parts)
# Or discuss with teammate if unsure

# STEP 4: After fixing all conflicts
git add .
git rebase --continue

# If you mess up, you can abort:
git rebase --abort
```

### Prevention: Why Conflicts Happen

| Cause | Prevention |
|-------|-----------|
| Edit same file | Follow file ownership rules |
| Forget to sync | Morning routine every day |
| Work too long without committing | Commit every 30-60 min |
| Both change shared types | Discuss before changing |
| Late night pushes | Always PR, never direct push to develop |

---

## 📁 File Ownership (Critical!)

### Pink Panther Owns (Jackie Chan: HANDS OFF!)

```
apps/api/**
├── app/
│   ├── main.py
│   ├── routers/*.py
│   ├── services/*.py
│   ├── models/*.py
│   └── schemas/*.py
├── alembic/**
├── tests/**
└── requirements.txt

scripts/**
infra/terraform/**
```

### Jackie Chan Owns (Pink Panther: HANDS OFF!)

```
apps/web/**
├── app/**
├── components/**
├── hooks/**
├── store/**
├── queries/**
├── lib/**
└── public/**

# Exception: .env.local is yours, don't commit it
```

### SHARED (Both Can Edit, But Must Discuss!)

```
packages/shared/**
├── src/types/*.ts
└── src/constants/*.ts

API_SPEC.md       # Pink Panther proposes, Jackie Chan reviews
DATABASE.md       # Pink Panther owns, Jackie Chan reads
TEAM_COLLABORATION.md  # Both update status
```

---

## 💬 Communication Rules

### Before Changing Shared Files

```
1. Send message: "Hey, I need to update Story type to add duration field"
2. Wait for: "OK go ahead" or "Can we discuss?"
3. Then make change
4. Notify: "Updated, please pull develop"
```

### Before Pushing Breaking Changes

```
Pink Panther: "Pushing new API format for /stories endpoint"
Jackie Chan: "OK, I'll update my queries after you merge"

# Pink merges, Jackie pulls, Jackie updates, Jackie pushes
```

---

## 🔧 Tool Setup (Do This Once)

### Git Configuration

```bash
# Set your identity
git config user.name "Pink Panther"
git config user.email "pink@bhashakahani.com"

# Enable colored output
git config color.ui auto

# Set default branch name
git config init.defaultBranch main

# Enable rebasing by default for pulls
git config pull.rebase true
```

### Git Aliases (Optional but Helpful)

```bash
# Add to ~/.bashrc or ~/.zshrc
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit

# Usage:
git st     # instead of git status
git co develop  # instead of git checkout develop
git br     # instead of git branch
git ci -m "message"  # instead of git commit -m "message"
```

---

## 📱 Daily Checklist App (Optional)

Create a `sync-checklist.md` in the repo that you both update:

```markdown
# Daily Sync Checklist - February 8, 2026

## Pink Panther
- [x] Morning sync complete
- [ ] Working on: Audio service
- [ ] Blockers: None
- [ ] Will push by: 6 PM

## Jackie Chan
- [x] Morning sync complete
- [ ] Working on: Story player page
- [ ] Blockers: Waiting for audio endpoint
- [ ] Will push by: 6 PM

## Sync Points Today
- [ ] 2:00 PM - API integration test
```

---

## ✅ Pre-Push Checklist

Before pushing your branch:

```bash
# 1. Is your code working?
# - Backend: uvicorn runs without errors
# - Frontend: npm run build succeeds

# 2. Did you commit everything?
git status  # Should show "nothing to commit, working tree clean"

# 3. Did you test?
# - Backend: curl endpoints work
# - Frontend: UI renders, no console errors

# 4. Are you on the right branch?
git branch  # Should show: * feature/PP-api-setup

# 5. Did you sync with develop today?
git log develop..feature/PP-api-setup  # Should be empty or only your commits

# 6. Push!
git push origin feature/PP-api-setup
```

---

## 🎯 Summary: Zero-Conflict Formula

```
1. MORNING: Pull develop, rebase your branch
2. DAY: Commit every 30-60 minutes  
3. EVENING: Push, create PR, request review
4. NEXT MORNING: Check if merged, create new branch
5. COMMUNICATION: Discuss before changing shared files
6. OWNERSHIP: Never touch teammate's files
```

**Follow this = ZERO CONFLICTS** ✅

---

## 🆘 Emergency Contacts

| Issue | Who to Ask | Response Time |
|-------|-----------|---------------|
| Git conflict | Teammate | Immediate |
| API question | Pink Panther | < 30 min |
| UI question | Jackie Chan | < 30 min |
| Shared type change | Both | Discuss first |
| Can't push | Check GitHub status | - |

---

**Remember: Communication prevents conflicts!** 🗣️
