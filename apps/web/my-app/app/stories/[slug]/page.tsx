'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, BookOpen, Clock, Play, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export default function StoryDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const { data: story, isLoading } = useQuery({
    queryKey: ['story', slug],
    queryFn: () => api.getStory(slug),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Skeleton className="h-8 w-32 mb-6" />
          <div className="grid md:grid-cols-2 gap-8">
            <Skeleton className="aspect-[4/3] rounded-lg" />
            <div className="space-y-4">
              <Skeleton className="h-10 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-12 w-48 mt-6" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
          <h1 className="text-2xl font-bold mb-2">Story Not Found</h1>
          <p className="text-muted-foreground mb-4">
            The story you're looking for doesn't exist.
          </p>
          <Button asChild>
            <Link href="/stories">Browse All Stories</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
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
          <div className="relative aspect-[4/3] rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-primary/5">
            {story.cover_image ? (
              <img
                src={story.cover_image}
                alt={story.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <BookOpen className="w-24 h-24 text-primary/40" />
              </div>
            )}
          </div>

          {/* Story Info */}
          <div className="flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-4">
              <Badge>Ages {story.age_range}</Badge>
              <Badge variant="secondary">{story.region}</Badge>
            </div>

            <h1 className="text-4xl font-bold mb-4">{story.title}</h1>
            <p className="text-lg text-muted-foreground mb-6">
              {story.description}
            </p>

            <div className="flex items-center gap-6 mb-6 text-muted-foreground">
              <span className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                {story.duration_min} minutes
              </span>
              <span className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                {story.character_count} characters
              </span>
            </div>

            {story.moral && (
              <div className="bg-muted p-4 rounded-lg mb-6">
                <p className="text-sm font-medium text-muted-foreground mb-1">Moral of the Story</p>
                <p className="italic">{story.moral}</p>
              </div>
            )}

            <Button size="lg" className="w-fit" asChild>
              <Link href={`/play/${story.id}`}>
                <Play className="w-5 h-5 mr-2" />
                Start Story
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Characters Section */}
      {story.characters && story.characters.length > 0 && (
        <div className="container mx-auto px-4 py-8 border-t">
          <h2 className="text-2xl font-bold mb-6">Characters</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {story.characters.map((character) => (
              <Card key={character.id}>
                <CardContent className="p-4 text-center">
                  <Avatar className="w-16 h-16 mx-auto mb-3">
                    <AvatarFallback className="bg-primary/10 text-primary">
                      {character.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="font-semibold">{character.name}</h3>
                  <p className="text-sm text-muted-foreground capitalize">
                    {character.voice_profile.replace('_', ' ')}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
