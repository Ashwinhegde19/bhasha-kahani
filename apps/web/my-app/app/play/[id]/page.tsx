'use client';

import { useParams, useSearchParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useRef, useCallback, Suspense } from 'react';
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
  Volume2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';
import { StoryNode } from '@/types';
import { cn } from '@/lib/utils';
import {
  DecorativeCorner,
  FloatingStar,
  FloatingSparkle,
} from '@/components/ui/decorative';

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

// Friendly display names for voice profiles
const VOICE_DISPLAY_NAMES: Record<string, string> = {
  warm_elderly: 'Storyteller',
  gentle_female: 'Gentle Voice',
  fierce_male: 'Bold Voice',
  young_energetic: 'Lively Voice',
  calm_male: 'Calm Voice',
  cheerful_female: 'Cheerful Voice',
};

// Get a friendly display name for a character
function getCharacterDisplayName(character: NonNullable<StoryNode['character']>): string {
  // Use the bulbul_speaker name (capitalized) as the primary display name
  if (character.bulbul_speaker) {
    return character.bulbul_speaker.charAt(0).toUpperCase() + character.bulbul_speaker.slice(1);
  }
  return character.name;
}

// Get voice style label
function getVoiceLabel(voiceProfile?: string): string {
  if (!voiceProfile) return 'narrator';
  return VOICE_DISPLAY_NAMES[voiceProfile] || voiceProfile.replace(/_/g, ' ');
}

// Check if an audio URL is actually playable (not empty or placeholder)
function isValidAudioUrl(url?: string | null): boolean {
  if (!url || !url.trim()) return false;
  // Reject placeholder URLs that point to non-existent CDNs
  if (url.includes('audio.bhashakahani.com') && url.includes('/generated/')) return false;
  return true;
}

function PlayStoryPageInner() {
  const params = useParams();
  const searchParams = useSearchParams();
  const storyId = params.id as string;
  const slugFromQuery = searchParams.get('slug');
  const queryClient = useQueryClient();
  const [playing, setPlaying] = useState(false);
  const [currentNodeIndex, setCurrentNodeIndex] = useState(0);
  const [hasListenedToLast, setHasListenedToLast] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);
  const usingSpeechRef = useRef(false);
  const autoPlayNextRef = useRef(false);
  const playingNodeIdRef = useRef<string | null>(null);

  // Refs to avoid stale closures in audio callbacks
  const currentNodeIndexRef = useRef(currentNodeIndex);
  const totalNodesRef = useRef(0);

  // Get user language preference
  const { language: storedLanguage, setLanguage } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState(storedLanguage || 'en');

  // Get story details - first resolve ID to slug, then fetch full story
  const { data: storySlug } = useQuery({
    queryKey: ['story-slug', storyId],
    queryFn: async () => {
      const stories = await api.listStories();
      const basicStory = stories.data.find((s) => s.id === storyId);
      return basicStory?.slug || null;
    },
    enabled: !!storyId && !slugFromQuery,
    staleTime: Infinity,
  });
  const resolvedStorySlug = slugFromQuery || storySlug;

  const { data: story, isLoading: storyLoading } = useQuery({
    queryKey: ['story', resolvedStorySlug, selectedLanguage],
    queryFn: () => api.getStory(resolvedStorySlug!, selectedLanguage),
    enabled: !!resolvedStorySlug,
  });

  // Get all story nodes (narration type)
  const narrationNodes: StoryNode[] =
    story?.nodes?.filter((n) => n.node_type === 'narration') ?? [];
  const currentNode = narrationNodes[currentNodeIndex];
  const totalNodes = narrationNodes.length;

  // Keep refs in sync
  currentNodeIndexRef.current = currentNodeIndex;
  totalNodesRef.current = totalNodes;

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
    retry: false,
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
    retry: false,
  });

  // Advance to next node (uses refs to avoid stale closure)
  const advanceToNextNode = useCallback(() => {
    if (autoPlayNextRef.current && currentNodeIndexRef.current < totalNodesRef.current - 1) {
      setCurrentNodeIndex((prev) => prev + 1);
    } else {
      setHasListenedToLast(true);
    }
  }, []);

  // Play audio
  const playAudio = useCallback((audioUrl: string, nodeId?: string) => {
    // Prevent duplicate play attempts on the same node
    if (nodeId && playingNodeIdRef.current === nodeId) return;

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      usingSpeechRef.current = false;
      speechRef.current = null;
    }

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    if (nodeId) playingNodeIdRef.current = nodeId;

    const audio = new Audio(audioUrl);
    audio.onended = () => {
      playingNodeIdRef.current = null;
      audioRef.current = null;
      setPlaying(false);
      advanceToNextNode();
    };
    audio.onerror = () => {
      playingNodeIdRef.current = null;
      audioRef.current = null;
      setPlaying(false);
    };
    audio.play().catch(() => {
      playingNodeIdRef.current = null;
      audioRef.current = null;
      setPlaying(false);
    });
    audioRef.current = audio;
    setPlaying(true);
  }, [advanceToNextNode]);

  const playFallbackSpeech = useCallback((text: string, langCode: string, nodeId?: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    if (!text.trim()) return;
    if (nodeId && playingNodeIdRef.current === nodeId) return;

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    window.speechSynthesis.cancel();

    if (nodeId) playingNodeIdRef.current = nodeId;
    usingSpeechRef.current = true;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang =
      langCode === 'hi'
        ? 'hi-IN'
        : langCode === 'kn'
        ? 'kn-IN'
        : 'en-IN';
    utterance.rate = 0.95;
    utterance.pitch = 1;

    utterance.onend = () => {
      usingSpeechRef.current = false;
      speechRef.current = null;
      playingNodeIdRef.current = null;
      setPlaying(false);
      advanceToNextNode();
    };

    utterance.onerror = () => {
      usingSpeechRef.current = false;
      speechRef.current = null;
      playingNodeIdRef.current = null;
      setPlaying(false);
    };

    speechRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setPlaying(true);
  }, [advanceToNextNode]);

  // Auto-play on node change
  useEffect(() => {
    if (autoPlayNextRef.current && !audioLoading && currentNode) {
      const timer = setTimeout(() => {
        // Only auto-play if nothing is currently playing
        const isHtmlAudioIdle =
          !audioRef.current || audioRef.current.paused || audioRef.current.ended;
        if (!isHtmlAudioIdle || usingSpeechRef.current) return;
        // Don't re-play the same node
        if (playingNodeIdRef.current === currentNode.id) return;

        if (isValidAudioUrl(nodeAudio?.audio_url)) {
          playAudio(nodeAudio!.audio_url, currentNode.id);
        } else if (currentNode.text) {
          playFallbackSpeech(currentNode.text, selectedLanguage, currentNode.id);
        }
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [currentNode?.id, audioLoading, nodeAudio, playAudio, playFallbackSpeech, currentNode, selectedLanguage]);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    usingSpeechRef.current = false;
    speechRef.current = null;
    playingNodeIdRef.current = null;
    setPlaying(false);
    autoPlayNextRef.current = false;
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleLanguageChange = (langCode: string) => {
    stopAudio();
    setSelectedLanguage(langCode);
    setLanguage(langCode);
    setCurrentNodeIndex(0);
    setHasListenedToLast(false);
    queryClient.invalidateQueries({ queryKey: ['story', resolvedStorySlug] });
    queryClient.invalidateQueries({ queryKey: ['node-audio'] });
  };

  const handlePlayPause = () => {
    // Stop speech synthesis
    if (
      playing &&
      usingSpeechRef.current &&
      typeof window !== 'undefined' &&
      'speechSynthesis' in window
    ) {
      window.speechSynthesis.cancel();
      usingSpeechRef.current = false;
      speechRef.current = null;
      playingNodeIdRef.current = null;
      setPlaying(false);
      autoPlayNextRef.current = false;
      return;
    }
    // Pause HTML audio
    if (playing && audioRef.current) {
      audioRef.current.pause();
      // Don't null audioRef so we can resume
      playingNodeIdRef.current = null;
      setPlaying(false);
      autoPlayNextRef.current = false;
      return;
    }
    // Resume paused HTML audio
    if (audioRef.current && audioRef.current.paused && !audioRef.current.ended) {
      audioRef.current.play().catch(() => {
        audioRef.current = null;
        playingNodeIdRef.current = null;
        setPlaying(false);
      });
      setPlaying(true);
      autoPlayNextRef.current = true;
      return;
    }
    // Start fresh playback
    if (!isValidAudioUrl(nodeAudio?.audio_url) && !currentNode?.text) return;
    autoPlayNextRef.current = true;
    playingNodeIdRef.current = null;
    // Clear any stale audio ref
    audioRef.current = null;
    if (isValidAudioUrl(nodeAudio?.audio_url)) {
      playAudio(nodeAudio!.audio_url, currentNode?.id);
    } else if (currentNode?.text) {
      playFallbackSpeech(currentNode.text, selectedLanguage, currentNode?.id);
    }
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 dark:from-background dark:via-background dark:to-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-card shadow-lg flex items-center justify-center">
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 dark:from-background dark:via-background dark:to-background flex items-center justify-center">
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

  const backHref = story.slug ? `/stories/${story.slug}` : '/stories';

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50/50 to-rose-50/30 dark:from-background dark:via-background dark:to-background flex flex-col">
      {/* Top Bar */}
      <header className="sticky top-0 z-20 glass-card border-b-0 relative">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          {/* Back + Title */}
          <div className="flex items-center gap-2 min-w-0">
            <Link
              href={backHref}
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
                className={cn(
                  'px-2.5 py-1 rounded-full text-xs font-semibold transition-all cursor-pointer',
                  selectedLanguage === lang.code
                    ? 'bg-gradient-to-r from-primary to-rose-500 text-white shadow-sm'
                    : 'bg-card dark:bg-secondary/50 text-muted-foreground hover:text-foreground',
                )}
              >
                <span className="mr-0.5">{lang.flag}</span>
                {lang.code.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Gradient bottom border */}
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary/40 to-transparent" aria-hidden="true" />

        {/* Progress Bar */}
        <div className="h-1 bg-muted/50">
          <div
            className="h-full transition-all duration-500 ease-out bg-gradient-to-r from-amber-400 via-orange-400 to-rose-400"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-6 max-w-2xl mx-auto w-full">
        {/* Part indicator */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">
            Part {currentNodeIndex + 1} of {totalNodes}
          </span>
          {/* Step dots with connecting lines */}
          {totalNodes <= 20 && (
            <div className="flex items-center ml-2">
              {narrationNodes.map((_, i) => (
                <div key={i} className="flex items-center">
                  <button
                    onClick={() => {
                      stopAudio();
                      setCurrentNodeIndex(i);
                      setHasListenedToLast(false);
                    }}
                    className={cn(
                      'rounded-full transition-all duration-300 relative z-10',
                      i === currentNodeIndex
                        ? 'w-4 h-4 bg-gradient-to-br from-primary to-rose-500 shadow-md ring-2 ring-primary/30'
                        : i < currentNodeIndex
                        ? 'w-3 h-3 bg-primary/50'
                        : 'w-3 h-3 bg-muted-foreground/20',
                    )}
                    aria-label={`Go to part ${i + 1}`}
                  />
                  {i < narrationNodes.length - 1 && (
                    <div
                      className={cn(
                        'w-3 h-0.5 transition-colors duration-300',
                        i < currentNodeIndex ? 'bg-primary/40' : 'bg-muted-foreground/10',
                      )}
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Character Badge with Speech Bubble */}
        {currentNode?.character && (
          <div className="flex items-center gap-3 mb-5 animate-fade-in">
            <div
              className={cn(
                'relative w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-lg ring ring-white/50 dark:ring-black/20',
                getCharacterColor(currentNode.character.name),
              )}
            >
              {getCharacterDisplayName(currentNode.character).charAt(0).toUpperCase()}
              {playing && (
                <span className="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full bg-card shadow flex items-center justify-center">
                  <Volume2 className="w-3 h-3 text-primary animate-pulse" />
                </span>
              )}
            </div>
            {/* Speech bubble */}
            <div className="relative glass-card rounded-xl px-4 py-2">
              <div className="absolute left-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 rotate-45 bg-[oklch(0.995_0.004_80_/_0.7)] dark:bg-[oklch(0.22_0.035_50_/_0.6)] border-l border-b border-[oklch(0.91_0.025_75_/_0.5)] dark:border-[oklch(1_0_0_/_0.08)]" />
              <p className="font-semibold text-base leading-tight relative z-10">
                {getCharacterDisplayName(currentNode.character)}
              </p>
              <p className="text-xs text-muted-foreground relative z-10">
                {LANGUAGES.find((l) => l.code === selectedLanguage)?.name} &middot;{' '}
                {getVoiceLabel(currentNode.character.voice_profile)}
              </p>
            </div>
          </div>
        )}

        {/* Story Text Card — Book Page */}
        <div className="w-full book-page rounded-2xl shadow-lg border border-border/40 p-6 sm:p-8 mb-6 min-h-[160px] flex items-center justify-center transition-all duration-300 relative overflow-hidden">
          <DecorativeCorner position="top-left" />
          <DecorativeCorner position="top-right" />
          <DecorativeCorner position="bottom-left" />
          <DecorativeCorner position="bottom-right" />
          {currentNode?.text ? (
            <p className="text-xl sm:text-2xl md:text-[1.7rem] leading-relaxed font-medium text-foreground/90 text-center story-text relative z-10">
              {currentNode.text}
            </p>
          ) : (
            <div className="flex flex-col items-center gap-2 text-muted-foreground/50 relative z-10">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-sm">Loading text...</span>
            </div>
          )}
        </div>

        {/* Audio & Navigation Controls */}
        <div className="flex items-center gap-4 mb-6">
          {/* Previous */}
          <button
            onClick={goToPrev}
            disabled={currentNodeIndex === 0}
            className="w-11 h-11 rounded-full glass-card shadow-sm flex items-center justify-center
                       text-muted-foreground hover:text-foreground hover:shadow-md
                       disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            aria-label="Previous part"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {/* Play / Pause / Loading */}
          {currentNode?.text ? (
            <button
              onClick={handlePlayPause}
              className={cn(
                'sparkle-button w-[4.5rem] h-[4.5rem] rounded-full shadow-lg flex items-center justify-center transition-all active:scale-95 cursor-pointer border-2',
                playing
                  ? 'bg-gradient-to-br from-primary to-rose-500 text-white border-primary/30 shadow-xl playing-glow'
                  : 'bg-card text-primary border-primary/10 hover:shadow-xl hover:border-primary/30',
              )}
              aria-label={playing ? 'Pause' : 'Play'}
            >
              {playing ? (
                <Pause className="w-7 h-7" />
              ) : (
                <Play className="w-7 h-7 ml-0.5" />
              )}
            </button>
          ) : (
            <div className="w-[4.5rem] h-[4.5rem] rounded-full glass-card shadow-lg border-2 border-border/20 flex items-center justify-center">
              <Loader2 className="w-7 h-7 animate-spin text-muted-foreground/50" />
            </div>
          )}

          {/* Next */}
          <button
            onClick={goToNext}
            disabled={currentNodeIndex >= totalNodes - 1}
            className="w-11 h-11 rounded-full glass-card shadow-sm flex items-center justify-center
                       text-muted-foreground hover:text-foreground hover:shadow-md
                       disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            aria-label="Next part"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Playback hint */}
        <p className="text-xs text-muted-foreground/60 font-medium mb-6">
          {audioLoading
            ? 'Preparing cloud audio... instant voice is available now'
            : playing
            ? 'Now playing — auto-advances to next part'
            : isValidAudioUrl(nodeAudio?.audio_url)
            ? 'Tap play to listen'
            : 'Tap play for instant voice mode'}
        </p>

        {/* Story Complete Celebration */}
        {isStoryComplete && (
          <div className="w-full book-page rounded-2xl shadow-xl p-8 text-center border border-primary/20 animate-scale-fade-in relative overflow-hidden">
            {/* Floating celebration sparkles */}
            <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
              <FloatingStar className="absolute top-4 left-8 text-amber-400/50" size={18} delay="0s" />
              <FloatingSparkle className="absolute top-6 right-12 text-rose-400/50" size={14} delay="0.3s" />
              <FloatingStar className="absolute bottom-8 left-16 text-primary/40" size={12} delay="0.7s" />
              <FloatingSparkle className="absolute bottom-4 right-8 text-violet-400/40" size={16} delay="1s" />
              <FloatingStar className="absolute top-12 left-[40%] text-amber-300/30" size={10} delay="1.5s" />
            </div>

            <div className="text-6xl mb-4 animate-gentle-bounce relative z-10">&#127881;</div>
            <h3 className="text-3xl font-extrabold gradient-text mb-2 relative z-10">Story Complete!</h3>
            <p className="text-muted-foreground mb-6 text-lg relative z-10">
              You finished <span className="font-bold">&quot;{story.title}&quot;</span> in{' '}
              {LANGUAGES.find((l) => l.code === selectedLanguage)?.name}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-3 relative z-10">
              <Button
                size="lg"
                className="sparkle-button rounded-full px-8 bg-gradient-to-r from-primary to-rose-500 text-white border-0"
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
                className="rounded-full px-8 glass-card"
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

      {/* Bottom Safe Area */}
      <footer className="py-3 text-center">
        <p className="text-[10px] text-muted-foreground/40 font-medium tracking-wide uppercase">
          Bhasha Kahani
        </p>
      </footer>
    </div>
  );
}

export default function PlayStoryPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50 dark:from-background dark:via-background dark:to-background flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-card shadow-lg flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
            <div>
              <p className="text-lg font-semibold text-foreground">Loading story...</p>
              <p className="text-sm text-muted-foreground">Preparing your experience</p>
            </div>
          </div>
        </div>
      }
    >
      <PlayStoryPageInner />
    </Suspense>
  );
}
