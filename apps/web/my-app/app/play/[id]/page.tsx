'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Volume2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function PlayStoryPage() {
  const params = useParams();
  const storyId = params.id as string;
  const [playing, setPlaying] = useState<string | null>(null);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  // Get story details with loading state
  const { data: story, isLoading: storyLoading, error: storyError } = useQuery({
    queryKey: ['story', storyId],
    queryFn: async () => {
      console.log('Fetching story list...');
      const stories = await api.listStories();
      console.log('Stories:', stories);
      const basicStory = stories.data.find((s: any) => s.id === storyId);
      if (!basicStory) {
        console.log('Story not found in list');
        return null;
      }
      console.log('Found basic story, fetching details...');
      return api.getStory(basicStory.slug);
    },
    enabled: !!storyId,
  });

  // Get all narration nodes (not just first)
  const narrationNodes = story?.nodes?.filter((n: any) => n.node_type === 'narration') || [];
  
  // Get full story audio
  const { data: audioData, isLoading: audioLoading } = useQuery({
    queryKey: ['full-story-audio', storyId, 'en'],
    queryFn: () => {
      if (!storyId) return null;
      return api.getFullStoryAudio(storyId, 'en');
    },
    enabled: !!storyId,
  });

  const playAudio = (url: string, nodeId: string) => {
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
    }

    if (playing === nodeId) {
      setPlaying(null);
      return;
    }

    const audio = new Audio(url);
    audio.onended = () => setPlaying(null);
    audio.play().catch(e => console.error('Audio play error:', e));
    setAudioElement(audio);
    setPlaying(nodeId);
  };

  if (storyLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading story...</p>
        </div>
      </div>
    );
  }

  if (storyError) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Error Loading Story</h1>
          <p className="text-muted-foreground mb-4">
            {storyError instanceof Error ? storyError.message : 'Failed to load story'}
          </p>
          <Button asChild>
            <Link href="/stories">Browse Stories</Link>
          </Button>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Story Not Found</h1>
          <p className="text-muted-foreground mb-4">ID: {storyId}</p>
          <Button asChild>
            <Link href="/stories">Browse Stories</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href={`/stories/${story.slug}`}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Story
          </Link>
        </Button>
      </div>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-center">{story.title}</h1>

        {audioLoading ? (
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading audio...</p>
          </div>
        ) : audioData?.audio_url ? (
          <Card className="max-w-2xl mx-auto">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <Button
                  size="lg"
                  onClick={() => playAudio(audioData.audio_url, 'start')}
                >
                  {playing === 'start' ? (
                    <Pause className="w-5 h-5 mr-2" />
                  ) : (
                    <Play className="w-5 h-5 mr-2" />
                  )}
                  {playing === 'start' ? 'Pause' : 'Play Narration'}
                </Button>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Volume2 className="w-5 h-5" />
                  <span>Audio from Sarvam AI</span>
                </div>
              </div>
              
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">Audio URL:</p>
                <a 
                  href={audioData.audio_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-blue-500 hover:underline break-all"
                >
                  {audioData.audio_url}
                </a>
              </div>

              <div className="mt-4 text-sm text-muted-foreground">
                <p>Status: Full Story Audio</p>
                <p>Total Nodes: {audioData.total_nodes}</p>
                <p>Duration: {Math.round(audioData.total_duration_sec)} seconds</p>
                <p>File Size: {((audioData.file_size || 0) / 1024).toFixed(1)} KB</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="text-center">
            <p className="text-muted-foreground">Audio not available</p>
          </div>
        )}

        {story?.nodes && (
          <Card className="max-w-2xl mx-auto mt-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold mb-4">Story Nodes ({story.nodes.length})</h2>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {story.nodes.map((node: any, index: number) => (
                  <div key={node.id} className="p-3 bg-muted rounded-lg">
                    <p className="text-sm font-medium text-muted-foreground mb-1">
                      Node {index + 1}: {node.character?.name || 'Narrator'}
                    </p>
                    <p className="text-sm">{node.text}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
