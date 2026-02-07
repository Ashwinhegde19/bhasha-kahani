# Jackie Chan - Frontend Lead Quick Reference

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
git checkout -b feature/B-nextjs-setup

# 3. Setup frontend
cd apps/web
npm install

# 4. Copy env and configure
cp .env.example .env.local
# Edit .env.local

# 5. Start dev server
npm run dev
# App at http://localhost:3000
```

---

## 📁 You Own These Files

```
apps/web/
├── app/
│   ├── (main)/
│   │   ├── page.tsx
│   │   ├── stories/
│   │   ├── play/[storyId]/
│   │   └── layout.tsx
│   ├── layout.tsx
│   └── manifest.ts
├── components/
│   ├── ui/              # shadcn components
│   ├── story/
│   ├── audio/
│   ├── choice/
│   ├── language/
│   └── layout/
├── hooks/
│   ├── useAudio.ts
│   ├── useStory.ts
│   └── useProgress.ts
├── store/
│   ├── userStore.ts
│   ├── storyStore.ts
│   └── audioStore.ts
├── queries/
│   ├── stories.ts
│   └── keys.ts
├── lib/
│   ├── api.ts
│   └── utils.ts
├── types/
│   └── *.ts
└── public/
    ├── sw.js
    └── manifest.json

packages/shared/ (coordinate with A)
```

---

## 🔑 Key Environment Variables

```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_OFFLINE=true

# Sentry (optional for local)
NEXT_PUBLIC_SENTRY_DSN=
```

---

## 📝 Daily Checklist

### Morning
- [ ] `git checkout develop && git pull`
- [ ] `git checkout feature/your-branch`
- [ ] `git rebase develop`
- [ ] Review Pink Panther's overnight PRs

### During Day
- [ ] Commit every 30-60 minutes
- [ ] Use format: `[JC] feat: description`
- [ ] Test UI in mobile view (F12 → toggle device)

### Evening
- [ ] Push branch: `git push origin feature/your-branch`
- [ ] Create PR to `develop`
- [ ] Tag Pink Panther for review
- [ ] Update task status in TEAM_COLLABORATION.md

---

## 🧪 Testing Your Components

```bash
# Build check
npm run build

# Type check
npm run type-check

# Lint check
npm run lint
```

---

## 🎨 shadcn/ui Commands

```bash
# Add new component
npx shadcn add button
npx shadcn add card
npx shadcn add slider
npx shadcn add dialog

# See all available
npx shadcn add --help
```

---

## 🆘 Emergency Contacts

- **Blocked by API question?** → Ping Pink Panther
- **Audio not playing?** → Check Howler.js docs
- **Build failing?** → Check TypeScript errors
- **Can't deploy?** → Check Vercel dashboard

---

## 📚 Useful Commands

```bash
# Dev server
npm run dev

# Build for production
npm run build

# Start production build
npm start

# Lint
npm run lint

# Type check
npx tsc --noEmit

# Deploy to Vercel
vercel --prod
```

---

## 📱 PWA Testing

1. Open Chrome DevTools (F12)
2. Go to Application → Manifest
3. Check icons, theme color
4. Go to Service Workers
5. Check "Offline" checkbox
6. Reload page - should still work

---

**Full details in TEAM_COLLABORATION.md**
