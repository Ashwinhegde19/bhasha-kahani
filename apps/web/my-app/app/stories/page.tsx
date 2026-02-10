'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Clock, Filter, Users, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api';
import { Story } from '@/types';
import { AGE_RANGES, LANGUAGES } from '@/lib/constants';
import { useUserStore } from '@/store';
import { cn } from '@/lib/utils';
import {
  SparkleGroup,
  DecorativeCorner,
  FloatingSparkle,
  FloatingStar,
  BackgroundParticles,
  IllustratedScene,
} from '@/components/ui/decorative';

function StoryCard({ story, index }: { story: Story; index: number }) {
  const [imgError, setImgError] = useState(false);

  return (
    <Link href={`/stories/${story.slug}`}>
      <div
        className={cn(
          'h-full rounded-2xl overflow-hidden bg-card shadow-sm hover:shadow-xl cursor-pointer group border border-border/30',
          'hover:-translate-y-3 hover-wiggle',
          'animate-slide-in-up relative',
          'transition-all duration-300',
        )}
        style={{ animationDelay: `${(index % 8) * 0.08}s` }}
      >
        <DecorativeCorner position="top-right" className="z-10" />
        <DecorativeCorner position="bottom-left" className="z-10" />

        {/* Cover Image Area */}
        <div className="relative aspect-[4/3] overflow-hidden">
          {story.cover_image && !imgError ? (
            <Image
              src={story.cover_image}
              alt={story.title}
              fill
              sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 25vw"
              className="object-cover transition-transform duration-500 group-hover:scale-110"
              onError={() => setImgError(true)}
            />
          ) : (
            <IllustratedScene index={index} />
          )}

          {/* Age Badge */}
          <Badge className="absolute top-3 left-3 bg-white/90 dark:bg-card/90 text-foreground shadow-sm animate-pop-in">
            Ages {story.age_range}
          </Badge>

          {/* Play hint on hover */}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
            <div className="w-14 h-14 rounded-full bg-white/90 dark:bg-card/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:scale-100 scale-50 shadow-lg">
              <Play className="w-6 h-6 text-primary ml-0.5" />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="font-semibold text-lg mb-1 line-clamp-1 group-hover:text-primary transition-colors">
            {story.title}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {story.description}
          </p>

          {/* Meta */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {story.duration_min} min
            </span>
            <span className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {story.character_count} characters
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

function StoryCardSkeleton() {
  return (
    <div className="h-full rounded-2xl overflow-hidden glass-card animate-pulse">
      <div className="aspect-[4/3] bg-gradient-to-br from-amber-100/50 to-rose-100/50 animate-shimmer" />
      <div className="p-4">
        <Skeleton className="h-6 w-3/4 mb-2" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-2/3 mb-3" />
        <div className="flex gap-4">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-20" />
        </div>
      </div>
    </div>
  );
}

export default function StoriesPage() {
  const [ageRange, setAgeRange] = useState<string>('all');
  const { language: selectedLanguage, setLanguage } = useUserStore();

  const { data: storiesData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['stories', { language: selectedLanguage, age_range: ageRange }],
    queryFn: () =>
      api.listStories({
        language: selectedLanguage,
        age_range: ageRange === 'all' ? undefined : ageRange,
      }),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const stories = storiesData?.data || [];
  const errorMessage =
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    typeof (error as { response?: { data?: { detail?: string } } }).response?.data
      ?.detail === 'string'
      ? (error as { response?: { data?: { detail?: string } } }).response?.data
          ?.detail || 'Failed to load stories'
      : error instanceof Error
      ? error.message
      : 'Failed to load stories';

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background dark:from-background dark:to-background relative">
      <BackgroundParticles />

      {/* Header */}
      <div className="container mx-auto px-4 pt-8 pb-4 relative z-10">
        <SparkleGroup className="opacity-50" dense />
        <h1 className="text-4xl md:text-5xl font-semibold mb-2 gradient-text relative z-10 animate-swing-in">
          Explore Stories
        </h1>
        <p className="text-muted-foreground text-lg relative z-10 animate-slide-in-up" style={{ animationDelay: '0.1s' }}>
          Folktales from across India
        </p>
      </div>

      {/* Filters */}
      <div className="container mx-auto px-4 pb-6 relative z-10">
        <div className="flex flex-wrap items-center gap-3 animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
          {/* Language Switcher */}
          <div className="flex items-center gap-1.5 mr-2">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={cn(
                  'px-4 py-2 rounded-full text-sm font-semibold transition-all cursor-pointer flex items-center gap-1.5 hover-jelly',
                  selectedLanguage === lang.code
                    ? 'bg-gradient-to-r from-primary to-rose-500 text-white shadow-md animate-gradient'
                    : 'glass-card text-muted-foreground hover:text-foreground hover:shadow-sm',
                )}
              >
                <span className="text-base">{lang.flag}</span>
                {lang.name}
              </button>
            ))}
          </div>

          <div className="w-px h-6 bg-border/50 hidden sm:block" />

          {/* Age Filter */}
          <div className="flex items-center gap-2 text-muted-foreground">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Age:</span>
          </div>

          <Select value={ageRange} onValueChange={setAgeRange}>
            <SelectTrigger className="w-[160px] glass-card rounded-full">
              <SelectValue placeholder="All Ages" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Ages</SelectItem>
              {AGE_RANGES.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {ageRange !== 'all' && (
            <Button variant="ghost" size="sm" className="rounded-full hover-jelly" onClick={() => setAgeRange('all')}>
              Clear
            </Button>
          )}
        </div>
      </div>

      {/* Stories Grid */}
      <div className="container mx-auto px-4 pb-12 relative z-10">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <StoryCardSkeleton key={i} />
            ))}
          </div>
        ) : isError ? (
          <div className="text-center py-16 animate-pop-in">
            <BookOpen className="w-16 h-16 mx-auto text-destructive/50 mb-4 animate-gentle-bounce" />
            <h3 className="text-xl font-semibold mb-2">Could not load stories</h3>
            <p className="text-muted-foreground mb-4">{errorMessage}</p>
            <Button className="rounded-full hover-jelly" onClick={() => refetch()}>Try again</Button>
          </div>
        ) : stories.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {stories.map((story, i) => (
              <StoryCard key={story.id} story={story} index={i} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 relative animate-pop-in">
            <div className="relative inline-block mb-6">
              <BookOpen className="w-20 h-20 mx-auto text-muted-foreground/30 animate-gentle-bounce" />
              <FloatingSparkle className="absolute -top-2 -right-2 text-primary/40" size={16} delay="0s" />
              <FloatingStar className="absolute -bottom-1 -left-3 text-amber-400/40" size={14} delay="0.5s" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No stories found</h3>
            <p className="text-muted-foreground">
              Try adjusting your filters or check back later for new stories.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
