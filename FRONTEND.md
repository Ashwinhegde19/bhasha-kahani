# Bhasha Kahani - Frontend Architecture

## 🎨 Frontend Overview

This document describes the complete frontend architecture for Bhasha Kahani using Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query, and Howler.js.

---

## 📁 Project Structure

```
apps/web/
├── app/                          # Next.js 15 App Router
│   ├── (main)/                   # Main layout group
│   │   ├── page.tsx              # Home/Language selection
│   │   ├── stories/
│   │   │   ├── page.tsx          # Story gallery
│   │   │   └── [slug]/
│   │   │       └── page.tsx      # Story detail
│   │   ├── play/
│   │   │   └── [storyId]/
│   │   │       └── page.tsx      # Story player
│   │   ├── bookmarks/
│   │   │   └── page.tsx          # User bookmarks
│   │   ├── progress/
│   │   │   └── page.tsx          # User progress
│   │   └── layout.tsx            # Main layout with nav
│   ├── api/                      # API routes (proxy)
│   │   └── [...path]/
│   │       └── route.ts
│   ├── layout.tsx                # Root layout
│   ├── loading.tsx               # Global loading
│   ├── error.tsx                 # Global error
│   ├── not-found.tsx             # 404 page
│   ├── manifest.ts               # PWA manifest
│   ├── robots.ts                 # Robots.txt
│   └── sitemap.ts                # Sitemap
│
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── slider.tsx
│   │   ├── avatar.tsx
│   │   ├── badge.tsx
│   │   ├── tooltip.tsx
│   │   ├── toast.tsx
│   │   ├── select.tsx
│   │   └── skeleton.tsx
│   │
│   ├── story/                    # Story components
│   │   ├── StoryCard.tsx         # Story card in gallery
│   │   ├── StoryGrid.tsx         # Grid of stories
│   │   ├── StoryDetail.tsx       # Story detail view
│   │   ├── StoryMeta.tsx         # Story metadata
│   │   └── StoryCover.tsx        # Story cover image
│   │
│   ├── audio/                    # Audio components
│   │   ├── AudioPlayer.tsx       # Main audio player
│   │   ├── AudioControls.tsx     # Play/pause/seek
│   │   ├── AudioProgress.tsx     # Progress bar
│   │   ├── AudioWaveform.tsx     # Visual waveform
│   │   ├── VolumeControl.tsx     # Volume slider
│   │   └── CharacterAvatar.tsx   # Character display
│   │
│   ├── choice/                   # Choice components
│   │   ├── ChoiceOverlay.tsx     # Choice modal/overlay
│   │   ├── ChoiceButton.tsx      # Individual choice
│   │   ├── ChoiceGrid.tsx        # Grid of choices
│   │   └── ChoiceFeedback.tsx    # Post-choice feedback
│   │
│   ├── language/                 # Language components
│   │   ├── LanguageSelector.tsx  # Language dropdown
│   │   ├── LanguageFlag.tsx      # Language flag/icon
│   │   └── CodeMixSlider.tsx     # Code-mix ratio slider
│   │
│   ├── layout/                   # Layout components
│   │   ├── Navbar.tsx            # Top navigation
│   │   ├── Footer.tsx            # Footer
│   │   ├── Sidebar.tsx           # Side navigation
│   │   ├── MobileNav.tsx         # Mobile navigation
│   │   └── PageTransition.tsx    # Page transitions
│   │
│   └── common/                   # Common components
│       ├── Logo.tsx
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── EmptyState.tsx
│       └── SEO.tsx
│
├── hooks/                        # Custom React hooks
│   ├── useAudio.ts               # Howler.js audio hook
│   ├── useStory.ts               # Story data hook
│   ├── useProgress.ts            # Progress tracking hook
│   ├── useLanguage.ts            # Language preference hook
│   ├── useBookmark.ts            # Bookmark operations hook
│   ├── useAnalytics.ts           # Analytics tracking hook
│   ├── useOffline.ts             # Offline detection hook
│   └── useMediaQuery.ts          # Responsive hook
│
├── lib/                          # Utilities
│   ├── utils.ts                  # General utilities
│   ├── api.ts                    # API client
│   ├── constants.ts              # Constants
│   ├── audio.ts                  # Audio utilities
│   ├── i18n.ts                   # Internationalization
│   └── validators.ts             # Input validation
│
├── store/                        # Zustand stores
│   ├── index.ts                  # Store exports
│   ├── userStore.ts              # User state
│   ├── storyStore.ts             # Story state
│   ├── audioStore.ts             # Audio state
│   ├── progressStore.ts          # Progress state
│   ├── languageStore.ts          # Language preferences
│   └── uiStore.ts                # UI state
│
├── types/                        # TypeScript types
│   ├── index.ts                  # Type exports
│   ├── story.ts                  # Story types
│   ├── audio.ts                  # Audio types
│   ├── user.ts                   # User types
│   ├── api.ts                    # API types
│   └── common.ts                 # Common types
│
├── queries/                      # TanStack Query
│   ├── stories.ts                # Story queries
│   ├── audio.ts                  # Audio queries
│   ├── user.ts                   # User queries
│   └── keys.ts                   # Query keys
│
├── public/                       # Static assets
│   ├── manifest.json
│   ├── favicon.ico
│   ├── icons/                    # PWA icons
│   ├── images/                   # Static images
│   └── sw.js                     # Service worker
│
├── styles/                       # Global styles
│   └── globals.css
│
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

---

## 🏗️ State Management

### Zustand Store Architecture

```typescript
// store/index.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// User Store
interface UserState {
  userId: string | null;
  anonymousId: string | null;
  preferences: UserPreferences;
  setUser: (user: User) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      immer((set) => ({
        userId: null,
        anonymousId: null,
        preferences: {
          language: 'hi',
          codeMixRatio: 0.3,
          volume: 0.8,
          autoPlay: true,
        },
        setUser: (user) => set((state) => {
          state.userId = user.id;
          state.anonymousId = user.anonymousId;
        }),
        updatePreferences: (prefs) => set((state) => {
          Object.assign(state.preferences, prefs);
        }),
      })),
      { name: 'user-store' }
    )
  )
);

// Story Store
interface StoryState {
  currentStory: Story | null;
  currentNode: StoryNode | null;
  choicesMade: ChoiceRecord[];
  isPlaying: boolean;
  setCurrentStory: (story: Story) => void;
  setCurrentNode: (node: StoryNode) => void;
  makeChoice: (choice: Choice) => void;
  setIsPlaying: (playing: boolean) => void;
  reset: () => void;
}

export const useStoryStore = create<StoryState>()(
  devtools(
    immer((set) => ({
      currentStory: null,
      currentNode: null,
      choicesMade: [],
      isPlaying: false,
      setCurrentStory: (story) => set((state) => {
        state.currentStory = story;
        state.currentNode = story.nodes.find(n => n.isStart) || null;
      }),
      setCurrentNode: (node) => set((state) => {
        state.currentNode = node;
      }),
      makeChoice: (choice) => set((state) => {
        state.choicesMade.push({
          nodeId: state.currentNode!.id,
          choiceKey: choice.key,
          timestamp: new Date().toISOString(),
        });
      }),
      setIsPlaying: (playing) => set((state) => {
        state.isPlaying = playing;
      }),
      reset: () => set((state) => {
        state.currentStory = null;
        state.currentNode = null;
        state.choicesMade = [];
        state.isPlaying = false;
      }),
    }))
  )
);

// Audio Store
interface AudioState {
  currentAudio: Howl | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  buffered: number;
  queue: AudioQueueItem[];
  setAudio: (audio: Howl) => void;
  play: () => void;
  pause: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  addToQueue: (item: AudioQueueItem) => void;
  clearQueue: () => void;
}

export const useAudioStore = create<AudioState>()(
  devtools(
    immer((set, get) => ({
      currentAudio: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 0.8,
      isMuted: false,
      buffered: 0,
      queue: [],
      setAudio: (audio) => set((state) => {
        state.currentAudio = audio;
        state.duration = audio.duration() || 0;
      }),
      play: () => {
        const { currentAudio } = get();
        if (currentAudio) {
          currentAudio.play();
          set((state) => { state.isPlaying = true; });
        }
      },
      pause: () => {
        const { currentAudio } = get();
        if (currentAudio) {
          currentAudio.pause();
          set((state) => { state.isPlaying = false; });
        }
      },
      seek: (time) => {
        const { currentAudio } = get();
        if (currentAudio) {
          currentAudio.seek(time);
          set((state) => { state.currentTime = time; });
        }
      },
      setVolume: (volume) => {
        const { currentAudio } = get();
        if (currentAudio) {
          currentAudio.volume(volume);
        }
        set((state) => { state.volume = volume; });
      },
      toggleMute: () => set((state) => {
        state.isMuted = !state.isMuted;
        if (state.currentAudio) {
          state.currentAudio.mute(state.isMuted);
        }
      }),
      addToQueue: (item) => set((state) => {
        state.queue.push(item);
      }),
      clearQueue: () => set((state) => {
        state.queue = [];
      }),
    }))
  )
);
```

---

## 🎵 Audio System (Howler.js)

### useAudio Hook

```typescript
// hooks/useAudio.ts
import { useEffect, useRef, useCallback } from 'react';
import { Howl, Howler } from 'howler';
import { useAudioStore } from '@/store';

interface UseAudioOptions {
  url: string;
  autoplay?: boolean;
  onEnd?: () => void;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

export function useAudio({ url, autoplay = false, onEnd, onLoad, onError }: UseAudioOptions) {
  const soundRef = useRef<Howl | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  const {
    setAudio,
    isPlaying,
    currentTime,
    duration,
    volume,
    setVolume,
    play,
    pause,
    seek,
  } = useAudioStore();

  useEffect(() => {
    // Initialize Howl
    const sound = new Howl({
      src: [url],
      html5: true, // Force HTML5 Audio for streaming
      preload: true,
      volume: volume,
      onload: () => {
        setAudio(sound);
        onLoad?.();
        if (autoplay) {
          play();
        }
      },
      onend: () => {
        onEnd?.();
      },
      onloaderror: (_id, error) => {
        onError?.(new Error(`Failed to load audio: ${error}`));
      },
      onplayerror: (_id, error) => {
        onError?.(new Error(`Failed to play audio: ${error}`));
      },
    });

    soundRef.current = sound;

    // Start progress tracking
    const updateProgress = () => {
      if (sound.playing()) {
        const current = sound.seek() as number;
        useAudioStore.setState({ currentTime: current });
        animationFrameRef.current = requestAnimationFrame(updateProgress);
      }
    };

    sound.on('play', () => {
      animationFrameRef.current = requestAnimationFrame(updateProgress);
    });

    sound.on('pause', () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    });

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      sound.unload();
    };
  }, [url]);

  const togglePlay = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);

  const seekTo = useCallback((time: number) => {
    seek(Math.max(0, Math.min(time, duration)));
  }, [duration, seek]);

  const skipForward = useCallback((seconds: number = 10) => {
    seekTo(currentTime + seconds);
  }, [currentTime, seekTo]);

  const skipBackward = useCallback((seconds: number = 10) => {
    seekTo(currentTime - seconds);
  }, [currentTime, seekTo]);

  return {
    isPlaying,
    currentTime,
    duration,
    volume,
    togglePlay,
    seekTo,
    skipForward,
    skipBackward,
    setVolume,
  };
}
```

### Audio Player Component

```typescript
// components/audio/AudioPlayer.tsx
'use client';

import { useEffect } from 'react';
import { useAudio } from '@/hooks/useAudio';
import { useAudioStore } from '@/store';
import { AudioControls } from './AudioControls';
import { AudioProgress } from './AudioProgress';
import { CharacterAvatar } from './CharacterAvatar';
import { VolumeControl } from './VolumeControl';

interface AudioPlayerProps {
  audioUrl: string;
  character?: Character;
  autoPlay?: boolean;
  onEnded?: () => void;
  onError?: (error: Error) => void;
}

export function AudioPlayer({
  audioUrl,
  character,
  autoPlay = false,
  onEnded,
  onError,
}: AudioPlayerProps) {
  const { isPlaying, currentTime, duration, togglePlay, seekTo } = useAudio({
    url: audioUrl,
    autoplay: autoPlay,
    onEnd: onEnded,
    onError,
  });

  return (
    <div className="w-full bg-card rounded-xl p-4 shadow-lg">
      {/* Character Info */}
      {character && (
        <div className="flex items-center gap-3 mb-4">
          <CharacterAvatar
            src={character.avatarUrl}
            name={character.name}
            size="md"
          />
          <div>
            <p className="font-medium text-foreground">{character.name}</p>
            <p className="text-sm text-muted-foreground">Speaking</p>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <AudioProgress
        currentTime={currentTime}
        duration={duration}
        onSeek={seekTo}
        className="mb-4"
      />

      {/* Controls */}
      <div className="flex items-center justify-between">
        <AudioControls
          isPlaying={isPlaying}
          onTogglePlay={togglePlay}
          onSkipBackward={() => seekTo(Math.max(0, currentTime - 10))}
          onSkipForward={() => seekTo(Math.min(duration, currentTime + 10))}
        />

        <VolumeControl />
      </div>
    </div>
  );
}
```

---

## 🔄 TanStack Query Integration

### Query Keys

```typescript
// queries/keys.ts
export const queryKeys = {
  stories: {
    all: ['stories'] as const,
    list: (filters: StoryFilters) => [...queryKeys.stories.all, 'list', filters] as const,
    detail: (slug: string) => [...queryKeys.stories.all, 'detail', slug] as const,
    nodes: (slug: string) => [...queryKeys.stories.all, 'nodes', slug] as const,
  },
  audio: {
    all: ['audio'] as const,
    url: (nodeId: string, language: string, codeMix: number) => 
      [...queryKeys.audio.all, nodeId, language, codeMix] as const,
  },
  user: {
    all: ['user'] as const,
    progress: () => [...queryKeys.user.all, 'progress'] as const,
    bookmarks: () => [...queryKeys.user.all, 'bookmarks'] as const,
  },
};
```

### Story Queries

```typescript
// queries/stories.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from './keys';

// List stories
export function useStories(filters: StoryFilters = {}) {
  return useQuery({
    queryKey: queryKeys.stories.list(filters),
    queryFn: () => api.stories.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get story detail
export function useStory(slug: string) {
  return useQuery({
    queryKey: queryKeys.stories.detail(slug),
    queryFn: () => api.stories.get(slug),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!slug,
  });
}

// Get story nodes
export function useStoryNodes(slug: string) {
  return useQuery({
    queryKey: queryKeys.stories.nodes(slug),
    queryFn: () => api.stories.getNodes(slug),
    staleTime: 10 * 60 * 1000,
    enabled: !!slug,
  });
}

// Make choice mutation
export function useMakeChoice() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ storySlug, nodeId, choiceKey }: MakeChoiceParams) =>
      api.choices.make(storySlug, nodeId, choiceKey),
    onSuccess: (_, variables) => {
      // Invalidate progress cache
      queryClient.invalidateQueries({ queryKey: queryKeys.user.progress() });
    },
  });
}
```

### Audio Queries

```typescript
// queries/audio.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { queryKeys } from './keys';

// Get audio URL
export function useAudioUrl(
  nodeId: string,
  language: string,
  codeMixRatio: number = 0,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: queryKeys.audio.url(nodeId, language, codeMixRatio),
    queryFn: () => api.audio.getUrl(nodeId, { language, codeMix: codeMixRatio }),
    staleTime: 30 * 24 * 60 * 60 * 1000, // 30 days (audio is immutable)
    cacheTime: 30 * 24 * 60 * 60 * 1000,
    enabled: options?.enabled !== false && !!nodeId && !!language,
  });
}
```

---

## 🎨 Component Examples

### Story Card

```typescript
// components/story/StoryCard.tsx
'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Users } from 'lucide-react';

interface StoryCardProps {
  story: Story;
}

export function StoryCard({ story }: StoryCardProps) {
  return (
    <Link href={`/stories/${story.slug}`}>
      <Card className="group overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1">
        {/* Cover Image */}
        <div className="relative aspect-[4/3] overflow-hidden">
          <Image
            src={story.coverImage}
            alt={story.title}
            fill
            className="object-cover transition-transform group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          
          {/* Age Badge */}
          <Badge className="absolute top-2 left-2 bg-primary/90">
            Ages {story.ageRange}
          </Badge>
          
          {/* Language Badge */}
          <Badge variant="secondary" className="absolute top-2 right-2">
            {story.availableLanguages.length} languages
          </Badge>
        </div>

        {/* Content */}
        <CardContent className="p-4">
          <h3 className="font-semibold text-lg mb-1 line-clamp-1">
            {story.title}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {story.description}
          </p>
          
          {/* Meta */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {story.durationMin} min
            </span>
            <span className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {story.characterCount} characters
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

### Choice Overlay

```typescript
// components/choice/ChoiceOverlay.tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ChoiceButton } from './ChoiceButton';
import { CharacterAvatar } from '@/components/audio/CharacterAvatar';

interface ChoiceOverlayProps {
  isOpen: boolean;
  node: StoryNode;
  choices: Choice[];
  onSelect: (choice: Choice) => void;
}

export function ChoiceOverlay({ isOpen, node, choices, onSelect }: ChoiceOverlayProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="w-full max-w-lg mx-4 bg-card rounded-2xl p-6 shadow-2xl"
          >
            {/* Character & Question */}
            <div className="flex items-start gap-4 mb-6">
              {node.character && (
                <CharacterAvatar
                  src={node.character.avatarUrl}
                  name={node.character.name}
                  size="lg"
                />
              )}
              <div>
                <p className="text-lg font-medium leading-relaxed">
                  {node.text}
                </p>
              </div>
            </div>

            {/* Choices */}
            <div className="space-y-3">
              {choices.map((choice, index) => (
                <ChoiceButton
                  key={choice.id}
                  choice={choice}
                  index={index}
                  onClick={() => onSelect(choice)}
                />
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

### Choice Button

```typescript
// components/choice/ChoiceButton.tsx
'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

interface ChoiceButtonProps {
  choice: Choice;
  index: number;
  onClick: () => void;
}

const choiceColors = [
  'bg-blue-500 hover:bg-blue-600',
  'bg-green-500 hover:bg-green-600',
  'bg-purple-500 hover:bg-purple-600',
];

export function ChoiceButton({ choice, index, onClick }: ChoiceButtonProps) {
  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: index * 0.1 }}
    >
      <Button
        variant="default"
        size="lg"
        className={`w-full justify-between text-left h-auto py-4 px-6 ${choiceColors[index % choiceColors.length]}`}
        onClick={onClick}
      >
        <span className="flex items-center gap-3">
          <span className="flex items-center justify-center w-8 h-8 rounded-full bg-white/20 font-bold">
            {choice.key}
          </span>
          <span className="text-lg">{choice.text}</span>
        </span>
        <ArrowRight className="w-5 h-5" />
      </Button>
    </motion.div>
  );
}
```

---

## 📱 PWA Configuration

### Manifest

```typescript
// app/manifest.ts
import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Bhasha Kahani',
    short_name: 'BhashaKahani',
    description: 'Multilingual Interactive Folktale Storyteller',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#f97316',
    icons: [
      {
        src: '/icons/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icons/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  };
}
```

### Service Worker

```javascript
// public/sw.js
const CACHE_NAME = 'bhasha-kahani-v1';
const STATIC_ASSETS = [
  '/',
  '/stories',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// Install - Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Fetch - Cache-first strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // API calls - Network first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clone);
          });
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }
  
  // Audio files - Cache first
  if (request.url.includes('.mp3') || request.url.includes('.wav')) {
    event.respondWith(
      caches.match(request).then((response) => {
        return (
          response ||
          fetch(request).then((fetchResponse) => {
            const clone = fetchResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, clone);
            });
            return fetchResponse;
          })
        );
      })
    );
    return;
  }
  
  // Static assets - Cache first
  event.respondWith(
    caches.match(request).then((response) => {
      return response || fetch(request);
    })
  );
});

// Background sync for analytics
self.addEventListener('sync', (event) => {
  if (event.tag === 'analytics-sync') {
    event.waitUntil(syncAnalytics());
  }
});

async function syncAnalytics() {
  const db = await openDB('analytics', 1);
  const events = await db.getAll('events');
  
  for (const event of events) {
    try {
      await fetch('/api/analytics/events', {
        method: 'POST',
        body: JSON.stringify(event),
      });
      await db.delete('events', event.id);
    } catch (error) {
      console.error('Failed to sync event:', error);
    }
  }
}
```

---

## 🎯 Performance Optimizations

### 1. Image Optimization

```typescript
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.bhashakahani.com',
      },
      {
        protocol: 'https',
        hostname: 'audio.bhashakahani.com',
      },
    ],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};
```

### 2. Code Splitting

```typescript
// Dynamic imports for heavy components
import dynamic from 'next/dynamic';

const AudioPlayer = dynamic(
  () => import('@/components/audio/AudioPlayer'),
  {
    ssr: false,
    loading: () => <AudioPlayerSkeleton />,
  }
);

const StoryPlayer = dynamic(
  () => import('@/components/story/StoryPlayer'),
  {
    loading: () => <StoryPlayerSkeleton />,
  }
);
```

### 3. Prefetching

```typescript
// Prefetch next audio segments
const prefetchNextAudio = useCallback((nextNodeId: string) => {
  const nextNode = story.nodes.find((n) => n.id === nextNodeId);
  if (nextNode?.audioUrl) {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = nextNode.audioUrl;
    document.head.appendChild(link);
  }
}, [story.nodes]);
```

---

## 📊 Bundle Analysis

```bash
# Analyze bundle size
npm run analyze

# Build with stats
npm run build:stats
```

---

**Version:** 1.0  
**Last Updated:** February 7, 2026
