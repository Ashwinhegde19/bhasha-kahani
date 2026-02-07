'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Clock, Filter, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
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
import { AGE_RANGES } from '@/lib/constants';

function StoryCard({ story }: { story: Story }) {
  return (
    <Link href={`/stories/${story.slug}`}>
      <Card className="h-full overflow-hidden transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer group">
        {/* Cover Image Placeholder */}
        <div className="relative aspect-[4/3] bg-gradient-to-br from-primary/20 to-primary/5 overflow-hidden">
          {story.cover_image ? (
            <img
              src={story.cover_image}
              alt={story.title}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <BookOpen className="w-16 h-16 text-primary/40" />
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          
          {/* Age Badge */}
          <Badge className="absolute top-2 left-2 bg-primary/90">
            Ages {story.age_range}
          </Badge>
        </div>

        {/* Content */}
        <CardContent className="p-4">
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
        </CardContent>
      </Card>
    </Link>
  );
}

function StoryCardSkeleton() {
  return (
    <Card className="h-full overflow-hidden">
      <Skeleton className="aspect-[4/3]" />
      <CardContent className="p-4">
        <Skeleton className="h-6 w-3/4 mb-2" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-2/3 mb-3" />
        <div className="flex gap-4">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-20" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function StoriesPage() {
  const [ageRange, setAgeRange] = useState<string>('all');
  
  const { data: storiesData, isLoading } = useQuery({
    queryKey: ['stories', { age_range: ageRange }],
    queryFn: () => api.listStories({ age_range: ageRange === 'all' ? undefined : ageRange }),
  });

  const stories = storiesData?.data || [];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-muted/30 border-b">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-2">Explore Stories</h1>
          <p className="text-muted-foreground">
            Discover interactive folktales from across India
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Filters:</span>
          </div>
          
          <Select value={ageRange} onValueChange={setAgeRange}>
            <SelectTrigger className="w-[180px]">
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
            <Button variant="ghost" size="sm" onClick={() => setAgeRange('all')}>
              Clear filters
            </Button>
          )}
        </div>
      </div>

      {/* Stories Grid */}
      <div className="container mx-auto px-4 pb-12">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <StoryCardSkeleton key={i} />
            ))}
          </div>
        ) : stories.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {stories.map((story) => (
              <StoryCard key={story.id} story={story} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
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
