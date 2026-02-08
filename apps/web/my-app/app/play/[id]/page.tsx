'use client';

import { useParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Play,
  Pause,
  Loader2,
  RotateCcw,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  SkipForward,
  Volume2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';

// Generate consistent color for character names dynamically
function getCharacterColor(name: string): string {
  const colors = [
    'bg-amber-500',
    'bg-orange-500',
    'bg-rose-500',
    'bg-emerald-500',
    'bg-sky-500',
    'bg-violet-500',
    'bg-pink-500',
    'bg-teal-500',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export default function PlayStoryPage() {
  const params = useParams();
  const storyId = params.id as string;
  const queryClient = useQueryClient();
  const [playing, setPlaying] = useState(false);
  const [currentNodeIndex, setCurrentNodeIndex] = useState(0);
  const [hasListenedToLast, setHasListenedToLast] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const autoPlayNextRef = useRef(false);

  // Get user language preference
  const { language: storedLanguage, setLanguage } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState(storedLanguage || 'en');

  // Get story details - first resolve ID to slug, then fetch full story
  const { data: storySlug } = useQuery({
    queryKey: ['story-slug', storyId],
    queryFn: async () => {
      const stories = await api.listStories();
      const basicStory = stories.data.find((s: any) => s.id === storyId);
      return basicStory?.slug || null;
    },
    enabled: !!storyId,
    staleTime: Infinity,
  });

  const { data: story, isLoading: storyLoading } = useQuery({
    queryKey: ['story', storySlug, selectedLanguage],
    queryFn: () => api.getStory(storySlug!, selectedLanguage),
    enabled: !!storySlug,
  });

  // Get all story nodes (narration type)
  const narrationNodes = story?.nodes?.filter((n: any) => n.node_type === 'narration') || [];
  const currentNode = narrationNodes[currentNodeIndex];
  const totalNodes = narrationNodes.length;

  // Get audio for current node
  const { data: nodeAudio, isLoading: audioLoading } = useQuery({
    queryKey: ['node-audio', currentNode?.id, selectedLanguage],
    queryFn: () => {
      if (!currentNode?.id) return null;
      return api.getAudioUrl(currentNode.id, {
        language: selectedLanguage,
        speaker: currentNode?.character?.bulbul_speaker || 'meera',
      });
    },
    enabled: !!currentNode?.id,
  });

  // Pre-fetch next node audio
  const nextNode = narrationNodes[currentNodeIndex + 1];
  useQuery({
    queryKey: ['node-audio', nextNode?.id, selectedLanguage],
    queryFn: () => {
      if (!nextNode?.id) return null;
      return api.getAudioUrl(nextNode.id, {
        language: selectedLanguage,
        speaker: nextNode?.character?.bulbul_speaker || 'meera',
      });
    },
    enabled: !!nextNode?.id && playing,
  });

  // Play audio
  const playAudio = useCallback((audioUrl: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const audio = new Audio(audioUrl);
    audio.onended = () => {
      setPlaying(false);
      if (autoPlayNextRef.current) {
        setCurrentNodeIndex((prev) => prev + 1);
      } else {
        setHasListenedToLast(true);
      }
    };
    audio.play().catch(() => setPlaying(false));
    audioRef.current = audio;
    setPlaying(true);
  }, []);

  // Auto-play on node change
  useEffect(() => {
    if (autoPlayNextRef.current && nodeAudio?.audio_url && !audioLoading && !playing) {
      const timer = setTimeout(() => playAudio(nodeAudio.audio_url), 100);
      return () => clearTimeout(timer);
    }
  }, [nodeAudio, audioLoading, playing, playAudio]);

  // Clamp index
  useEffect(() => {
    if (currentNodeIndex >= narrationNodes.length && narrationNodes.length > 0) {
      autoPlayNextRef.current = false;
      setCurrentNodeIndex(narrationNodes.length - 1);
    }
  }, [currentNodeIndex, narrationNodes.length]);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setPlaying(false);
    autoPlayNextRef.current = false;
  }, []);

  const handleLanguageChange = (langCode: string) => {
    setSelectedLanguage(langCode);
    setLanguage(langCode);
    setCurrentNodeIndex(0);
    stopAudio();
    setHasListenedToLast(false);
    queryClient.invalidateQueries({ queryKey: ['story', storySlug] });
    queryClient.invalidateQueries({ queryKey: ['node-audio'] });
  };

  const handlePlayPause = () => {
    if (playing && audioRef.current) {
      audioRef.current.pause();
      setPlaying(false);
      autoPlayNextRef.current = false;
      return;
    }
    if (audioRef.current && audioRef.current.paused && !audioRef.current.ended) {
      audioRef.current.play().catch(() => setPlaying(false));
      setPlaying(true);
      autoPlayNextRef.current = true;
      return;
    }
    if (!nodeAudio?.audio_url) return;
    autoPlayNextRef.current = true;
    playAudio(nodeAudio.audio_url);
  };

  const goToPrev = () => {
    if (currentNodeIndex > 0) {
      stopAudio();
      setCurrentNodeIndex((prev) => prev - 1);
      setHasListenedToLast(false);
    }
  };

  const goToNext = () => {
    if (currentNodeIndex < totalNodes - 1) {
      stopAudio();
      setCurrentNodeIndex((prev) => prev + 1);
      setHasListenedToLast(false);
    }
  };

  const isStoryComplete =
    currentNodeIndex === totalNodes - 1 && !playing && hasListenedToLast;
  const progressPercent =
    totalNodes > 0 ? ((currentNodeIndex + 1) / totalNodes) * 100 : 0;

  // --- Loading State ---
  if (storyLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-white/80 shadow-lg flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
          <div>
            <p className="text-lg font-semibold text-foreground">Loading story...</p>
            <p className="text-sm text-muted-foreground">Preparing your experience</p>
          </div>
        </div>
      </div>
    );
  }

  // --- Not Found ---
  if (!story) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 flex items-center justify-center">
        <div className="text-center space-y-4 px-6">
          <BookOpen className="w-20 h-20 mx-auto text-primary/30" />
          <h1 className="text-2xl font-bold">Story Not Found</h1>
          <p className="text-muted-foreground">This story may have been removed or the link is incorrect.</p>
          <Button size="lg" className="rounded-full px-8" asChild>
            <Link href="/stories">Browse Stories</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50/50 to-rose-50/30 flex flex-col">
      {/* ─── Top Bar ─── */}
      <header className="sticky top-0 z-20 backdrop-blur-md bg-white/60 border-b border-amber-100/60">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          {/* Back + Title */}
          <div className="flex items-center gap-2 min-w-0">
            <Link
              href={`/stories/${story.slug}`}
              className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors shrink-0"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm hidden sm:inline">Back</span>
            </Link>
            <span className="text-muted-foreground/40 hidden sm:inline">|</span>
            <h1 className="text-sm font-semibold truncate text-foreground/80">
              {story.title}
            </h1>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center gap-1">
            {LANGUAGES.filter((lang) =>
              story.available_languages?.includes(lang.code)
            ).map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`
                  px-2.5 py-1 rounded-full text-xs font-semibold transition-all
                  ${
                    selectedLanguage === lang.code
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'bg-white/80 text-muted-foreground hover:bg-white hover:text-foreground'
                  }
                `}
              >
                <span className="mr-0.5">{lang.flag}</span>
                {lang.code.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-1 bg-amber-100/50">
          <div
            className="h-full transition-all duration-500 ease-out bg-gradient-to-r from-amber-400 via-orange-400 to-rose-400"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </header>

      {/* ─── Main Content ─── */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-6 max-w-2xl mx-auto w-full">
        {/* Part indicator */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">
            Part {currentNodeIndex + 1} of {totalNodes}
          </span>
          {/* Step dots for short stories */}
          {totalNodes <= 20 && (
            <div className="flex items-center gap-0.5 ml-2">
              {narrationNodes.map((_: any, i: number) => (
                <button
                  key={i}
                  onClick={() => {
                    stopAudio();
                    setCurrentNodeIndex(i);
                    setHasListenedToLast(false);
                  }}
                  className={`
                    rounded-full transition-all duration-300
                    ${
                      i === currentNodeIndex
                        ? 'w-5 h-2 bg-primary'
                        : i < currentNodeIndex
                        ? 'w-2 h-2 bg-primary/40'
                        : 'w-2 h-2 bg-muted-foreground/20'
                    }
                  `}
                  aria-label={`Go to part ${i + 1}`}
                />
              ))}
            </div>
          )}
        </div>

        {/* Character Badge */}
        {currentNode?.character && (
          <div className="flex items-center gap-3 mb-5 animate-fade-in">
            <div
              className={`
                relative w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-md
                ${getCharacterColor(currentNode.character.name)}
              `}
            >
              {currentNode.character.name.charAt(0).toUpperCase()}
              {playing && (
                <span className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full bg-white shadow flex items-center justify-center">
                  <Volume2 className="w-2.5 h-2.5 text-primary animate-pulse" />
                </span>
              )}
            </div>
            <div>
              <p className="font-semibold text-base leading-tight">
                {currentNode.character.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {LANGUAGES.find((l) => l.code === selectedLanguage)?.name} &middot;{' '}
                {currentNode.character.voice_profile?.replace('_', ' ') || 'narrator'}
              </p>
            </div>
          </div>
        )}

        {/* ─── Story Text Card ─── */}
        <div
          className="w-full bg-white/90 backdrop-blur rounded-2xl shadow-[0_2px_24px_-4px_rgba(0,0,0,0.08)] 
                     border border-white/60 p-6 sm:p-8 mb-6 min-h-[160px] flex items-center justify-center
                     transition-all duration-300"
        >
          {currentNode?.text ? (
            <p className="text-xl sm:text-2xl md:text-[1.7rem] leading-relaxed font-medium text-foreground/90 text-center story-text">
              {currentNode.text}
            </p>
          ) : (
            <div className="flex flex-col items-center gap-2 text-muted-foreground/50">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-sm">Loading text...</span>
            </div>
          )}
        </div>

        {/* ─── Audio & Navigation Controls ─── */}
        <div className="flex items-center gap-4 mb-6">
          {/* Previous */}
          <button
            onClick={goToPrev}
            disabled={currentNodeIndex === 0}
            className="w-11 h-11 rounded-full bg-white/80 shadow-sm border border-white/60 flex items-center justify-center
                       text-muted-foreground hover:text-foreground hover:bg-white hover:shadow-md
                       disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            aria-label="Previous part"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {/* Play / Pause / Loading */}
          {audioLoading ? (
            <div className="w-16 h-16 rounded-full bg-white shadow-lg border-2 border-primary/20 flex items-center justify-center">
              <Loader2 className="w-7 h-7 animate-spin text-primary" />
            </div>
          ) : nodeAudio?.audio_url ? (
            <button
              onClick={handlePlayPause}
              className={`
                w-16 h-16 rounded-full shadow-lg flex items-center justify-center transition-all
                active:scale-95 cursor-pointer border-2
                ${
                  playing
                    ? 'bg-primary text-primary-foreground border-primary/30 shadow-primary/20 shadow-xl playing-glow'
                    : 'bg-white text-primary border-primary/10 hover:shadow-xl hover:border-primary/30'
                }
              `}
              aria-label={playing ? 'Pause' : 'Play'}
            >
              {playing ? (
                <Pause className="w-7 h-7" />
              ) : (
                <Play className="w-7 h-7 ml-0.5" />
              )}
            </button>
          ) : (
            <div className="w-16 h-16 rounded-full bg-white/60 shadow-lg border-2 border-muted/20 flex items-center justify-center">
              <Loader2 className="w-7 h-7 animate-spin text-muted-foreground/50" />
            </div>
          )}

          {/* Next */}
          <button
            onClick={goToNext}
            disabled={currentNodeIndex >= totalNodes - 1}
            className="w-11 h-11 rounded-full bg-white/80 shadow-sm border border-white/60 flex items-center justify-center
                       text-muted-foreground hover:text-foreground hover:bg-white hover:shadow-md
                       disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            aria-label="Next part"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Playback hint */}
        <p className="text-xs text-muted-foreground/60 font-medium mb-6">
          {audioLoading
            ? 'Preparing audio...'
            : playing
            ? 'Now playing — auto-advances to next part'
            : 'Tap play to listen'}
        </p>

        {/* ─── Story Complete ─── */}
        {isStoryComplete && (
          <div
            className="w-full bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl shadow-lg 
                       p-8 text-center border border-amber-200/40 animate-fade-in"
          >
            <div className="text-5xl mb-3">🎉</div>
            <h3 className="text-2xl font-bold text-foreground mb-1">Story Complete!</h3>
            <p className="text-muted-foreground mb-6">
              You finished <span className="font-semibold">&quot;{story.title}&quot;</span> in{' '}
              {LANGUAGES.find((l) => l.code === selectedLanguage)?.name}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3">
              <Button
                size="lg"
                className="rounded-full px-6"
                onClick={() => {
                  setCurrentNodeIndex(0);
                  setHasListenedToLast(false);
                }}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Play Again
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="rounded-full px-6 bg-white/80"
                asChild
              >
                <Link href="/stories">
                  <BookOpen className="w-4 h-4 mr-2" />
                  More Stories
                </Link>
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* ─── Bottom Safe Area / Mini Player Info ─── */}
      <footer className="py-3 text-center">
        <p className="text-[10px] text-muted-foreground/40 font-medium tracking-wide uppercase">
          Bhasha Kahani
        </p>
      </footer>
    </div>
  );
}
