'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft, BookOpen, Clock, Globe, Play, Users, Quote } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';

const AVATAR_COLORS = [
  'bg-amber-400',
  'bg-rose-400',
  'bg-sky-400',
  'bg-emerald-400',
  'bg-violet-400',
  'bg-orange-400',
];

export default function StoryDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const { language: selectedLanguage } = useUserStore();

  const { data: story, isLoading, error, refetch } = useQuery({
    queryKey: ['story', slug, selectedLanguage],
    queryFn: () => api.getStory(slug, selectedLanguage),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background dark:from-background dark:to-background">
        <div className="container mx-auto px-4 py-8">
          <Skeleton className="h-8 w-32 mb-6" />
          <div className="grid md:grid-cols-2 gap-8">
            <Skeleton className="aspect-[4/3] rounded-2xl" />
            <div className="space-y-4">
              <Skeleton className="h-10 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-14 w-48 mt-6 rounded-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background dark:from-background dark:to-background flex items-center justify-center">
        <div className="text-center px-6">
          <BookOpen className="w-16 h-16 mx-auto text-destructive/50 mb-4" />
          <h1 className="text-2xl font-bold mb-2">Error Loading Story</h1>
          <p className="text-muted-foreground mb-4">
            {error instanceof Error ? error.message : 'Failed to load story'}
          </p>
          <div className="flex justify-center gap-3">
            <Button onClick={() => refetch()}>Try Again</Button>
            <Button variant="outline" asChild>
              <Link href="/stories">Browse All Stories</Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background dark:from-background dark:to-background flex items-center justify-center">
        <div className="text-center px-6">
          <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
          <h1 className="text-2xl font-bold mb-2">Story Not Found</h1>
          <p className="text-muted-foreground mb-4">
            The story you&apos;re looking for doesn&apos;t exist.
          </p>
          <Button size="lg" asChild>
            <Link href="/stories">Browse All Stories</Link>
          </Button>
        </div>
      </div>
    );
  }

  const narrationCount =
    story.nodes?.filter((n) => n.node_type === 'narration').length ?? 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background dark:from-background dark:to-background">
      {/* Back Button */}
      <div className="container mx-auto px-4 py-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/stories">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Stories
          </Link>
        </Button>
      </div>

      {/* Story Header */}
      <div className="container mx-auto px-4 pb-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Cover Image */}
          <div className="relative aspect-[4/3] rounded-2xl overflow-hidden bg-gradient-to-br from-amber-200/60 to-orange-200/60 shadow-lg">
            {story.cover_image ? (
              <Image
                src={story.cover_image}
                alt={story.title}
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                className="object-cover"
                priority
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <BookOpen className="w-24 h-24 text-white/60" />
              </div>
            )}
          </div>

          {/* Story Info */}
          <div className="flex flex-col justify-center">
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <Badge className="bg-primary/15 text-primary border-primary/20 dark:bg-primary/20">
                Ages {story.age_range}
              </Badge>
              {story.region && (
                <Badge variant="secondary">{story.region}</Badge>
              )}
            </div>

            <h1 className="text-3xl md:text-4xl font-bold mb-4">{story.title}</h1>
            <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
              {story.description}
            </p>

            <div className="flex flex-wrap items-center gap-5 mb-6 text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                {story.duration_min} min
              </span>
              <span className="flex items-center gap-1.5">
                <Users className="w-4 h-4" />
                {story.character_count} characters
              </span>
              {narrationCount > 0 && (
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4" />
                  {narrationCount} parts
                </span>
              )}
            </div>

            {/* Available Languages */}
            {story.available_languages && story.available_languages.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 mb-6">
                <Globe className="w-4 h-4 text-muted-foreground" />
                {story.available_languages.map((langCode) => {
                  const lang = LANGUAGES.find((l) => l.code === langCode);
                  return (
                    <Badge key={langCode} variant="outline" className="text-xs">
                      {lang?.flag} {lang?.name || langCode}
                    </Badge>
                  );
                })}
              </div>
            )}

            {story.moral && (
              <div className="bg-card dark:bg-secondary/50 border border-border/50 p-5 rounded-xl mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <Quote className="w-4 h-4 text-primary" />
                  <p className="text-sm font-semibold text-primary">Moral of the Story</p>
                </div>
                <p className="italic text-foreground/80 leading-relaxed">{story.moral}</p>
              </div>
            )}

            <Button
              size="lg"
              className="w-fit px-8 py-6 text-lg rounded-full shadow-lg hover:shadow-xl transition-all"
              asChild
            >
              <Link href={`/play/${story.id}?slug=${story.slug}`}>
                <Play className="w-6 h-6 mr-2" />
                Start Listening
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Characters Section */}
      {story.characters && story.characters.length > 0 && (
        <div className="container mx-auto px-4 py-8 border-t border-border/30">
          <h2 className="text-2xl font-bold mb-6">Characters</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {story.characters.map((character, i) => (
              <div
                key={character.id}
                className="bg-card dark:bg-secondary/50 rounded-2xl p-5 text-center shadow-sm border border-border/30"
              >
                <div
                  className={`
                    w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center text-white text-2xl font-bold
                    ${AVATAR_COLORS[i % AVATAR_COLORS.length]}
                  `}
                >
                  {character.name.charAt(0).toUpperCase()}
                </div>
                <h3 className="font-bold">{character.name}</h3>
                <p className="text-sm text-muted-foreground capitalize">
                  {character.voice_profile?.replace('_', ' ') || 'narrator'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
