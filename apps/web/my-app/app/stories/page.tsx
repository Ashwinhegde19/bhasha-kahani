'use client';

import { useState } from 'react';
import Link from 'next/link';
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
import { AGE_RANGES } from '@/lib/constants';

// Rotating card gradient backgrounds
const CARD_GRADIENTS = [
  'from-amber-200/60 to-orange-200/60',
  'from-rose-200/60 to-pink-200/60',
  'from-sky-200/60 to-cyan-200/60',
  'from-emerald-200/60 to-teal-200/60',
  'from-violet-200/60 to-purple-200/60',
  'from-yellow-200/60 to-amber-200/60',
];

function StoryCard({ story, index }: { story: Story; index: number }) {
  const gradient = CARD_GRADIENTS[index % CARD_GRADIENTS.length];

  return (
    <Link href={`/stories/${story.slug}`}>
      <div className="h-full rounded-2xl overflow-hidden bg-white shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer group">
        {/* Cover Image Area */}
        <div className={`relative aspect-[4/3] bg-gradient-to-br ${gradient} overflow-hidden`}>
          {story.cover_image ? (
            <img
              src={story.cover_image}
              alt={story.title}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <BookOpen className="w-16 h-16 text-white/60" />
            </div>
          )}
          
          {/* Age Badge */}
          <Badge className="absolute top-3 left-3 bg-white/90 text-foreground shadow-sm">
            Ages {story.age_range}
          </Badge>

          {/* Play hint on hover */}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
            <div className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">
              <Play className="w-6 h-6 text-primary ml-0.5" />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="font-bold text-lg mb-1 line-clamp-1 group-hover:text-primary transition-colors">
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
    <div className="h-full rounded-2xl overflow-hidden bg-white">
      <Skeleton className="aspect-[4/3]" />
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
  
  const { data: storiesData, isLoading } = useQuery({
    queryKey: ['stories', { age_range: ageRange }],
    queryFn: () => api.listStories({ age_range: ageRange === 'all' ? undefined : ageRange }),
  });

  const stories = storiesData?.data || [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-background">
      {/* Header */}
      <div className="container mx-auto px-4 pt-6 pb-4">
        <h1 className="text-3xl md:text-4xl font-bold mb-1">Explore Stories</h1>
        <p className="text-muted-foreground text-lg">
          Folktales from across India
        </p>
      </div>

      {/* Filters */}
      <div className="container mx-auto px-4 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Age:</span>
          </div>
          
          <Select value={ageRange} onValueChange={setAgeRange}>
            <SelectTrigger className="w-[160px] bg-white/80 rounded-xl">
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
              Clear
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
            {stories.map((story, i) => (
              <StoryCard key={story.id} story={story} index={i} />
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
