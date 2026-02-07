# Jackie Chan - Frontend Lead Quick Reference

## 🎯 10-Hour Sprint Mode

**Goal:** Complete frontend in 10 hours  
**Focus:** Speed + Quality  
**Read:** `10_HOUR_SPRINT.md` for full timeline

---

## ⚡ Hour-by-Hour Checklist

### Hour 1-2: Foundation
```bash
# Next.js setup (30 min)
cd apps/web
npx create-next-app@latest . --typescript --tailwind --app

# shadcn/ui (30 min)
npx shadcn@latest init
npx shadcn add button card slider avatar badge dialog

# Dependencies (30 min)
npm install zustand @tanstack/react-query howler axios
npm install -D @types/howler

# Structure (30 min)
# Create folders: components/, hooks/, store/, queries/
```

### Hour 3-4: Core UI
```bash
# API client (30 min)
# - Setup axios
# - TanStack Query provider

# Components (90 min)
# - StoryCard.tsx
# - StoryGrid.tsx
# - /stories page

# State (30 min)
# - userStore.ts
# - storyStore.ts
# - audioStore.ts
```

### Hour 5-6: Audio Player
```bash
# Howler integration (60 min)
# - useAudio.ts hook
# - AudioPlayer.tsx component

# Player page (60 min)
# - /play/[storyId]/page.tsx
# - Connect to API
# - Test audio playback
```

### Hour 7-8: Choices + Polish
```bash
# Choice UI (90 min)
# - ChoiceOverlay.tsx
# - ChoiceButton.tsx
# - Branch navigation

# Language + PWA (30 min)
# - LanguageSelector.tsx
# - CodeMixSlider.tsx
# - PWA manifest
```

### Hour 9-10: Mobile + Deploy
```bash
# Mobile (60 min)
# - Responsive design
# - Touch controls

# Deploy (90 min)
vercel --prod
# Update API URL
# Test production
```

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd bhasha-kahani
git checkout -b feature/JC-sprint

# Setup frontend
cd apps/web
npm install
cp .env.example .env.local
# Edit .env.local

# Start
npm run dev
# Open http://localhost:3000
```

---

## 🔑 Environment Variables (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_OFFLINE=true

NEXT_PUBLIC_SENTRY_DSN=
```

**Production:**
```env
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

---

## 📝 Git Commands (10-Hour Sprint)

```bash
# Every 1-2 hours
git add .
git commit -m "[JC] feat: what you built"

# At sync points
git push origin feature/JC-sprint

# Pink needs your changes?
git checkout develop
git merge feature/JC-sprint
git push origin develop
```

---

## 🎨 Key Components

### StoryCard.tsx
```tsx
'use client';
import { Card, CardContent } from '@/components/ui/card';

export function StoryCard({ story }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <img src={story.coverImage} alt={story.title} />
      <CardContent>
        <h3>{story.title}</h3>
        <p>{story.description}</p>
      </CardContent>
    </Card>
  );
}
```

### AudioPlayer.tsx
```tsx
'use client';
import { useAudio } from '@/hooks/useAudio';

export function AudioPlayer({ audioUrl }) {
  const { isPlaying, togglePlay, progress } = useAudio(audioUrl);
  
  return (
    <div>
      <button onClick={togglePlay}>
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <progress value={progress} max={100} />
    </div>
  );
}
```

---

## 🧪 Quick Tests

```bash
# Build check
npm run build

# Type check
npx tsc --noEmit

# Lint
npm run lint
```

---

## 🆘 Emergency Help

| Issue | Fix |
|-------|-----|
| API not connecting | Check NEXT_PUBLIC_API_URL, CORS |
| Audio not playing | Check Howler.js setup, audio URL |
| Build failing | Check TypeScript errors |
| Hydration error | Add 'use client' directive |
| Deploy failing | Check Vercel logs |

---

## 📱 PWA Quick Setup

```typescript
// app/manifest.ts
export default function manifest() {
  return {
    name: 'Bhasha Kahani',
    short_name: 'BhashaKahani',
    start_url: '/',
    display: 'standalone',
    background_color: '#fff',
    theme_color: '#f97316',
  };
}
```

```javascript
// public/sw.js
const CACHE_NAME = 'bhasha-v1';
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME));
});
```

---

## 🎵 Howler.js Pattern

```typescript
// hooks/useAudio.ts
import { useEffect, useRef } from 'react';
import { Howl } from 'howler';

export function useAudio(url: string) {
  const soundRef = useRef<Howl | null>(null);
  
  useEffect(() => {
    soundRef.current = new Howl({
      src: [url],
      html5: true,
    });
    
    return () => soundRef.current?.unload();
  }, [url]);
  
  const play = () => soundRef.current?.play();
  const pause = () => soundRef.current?.pause();
  
  return { play, pause };
}
```

---

## ✅ Success Checklist

- [ ] Story gallery displays
- [ ] Audio plays correctly
- [ ] Choices work
- [ ] Language switching works
- [ ] Mobile responsive
- [ ] PWA installable
- [ ] Deployed to Vercel

**Full details in 10_HOUR_SPRINT.md**
