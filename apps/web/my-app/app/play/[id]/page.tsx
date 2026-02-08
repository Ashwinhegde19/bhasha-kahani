'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Volume2, Loader2, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';

export default function PlayStoryPage() {
  const params = useParams();
  const storyId = params.id as string;
  const [playing, setPlaying] = useState<string | null>(null);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  
  // Get user language preference
  const { user } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  
  // Update language when user data loads
  useEffect(() => {
    if (user?.preferences?.language) {
      setSelectedLanguage(user.preferences.language);
    }
  }, [user]);

  // Get story details with loading state
  const { data: story, isLoading: storyLoading, error: storyError } = useQuery({
    queryKey: ['story', storyId],
    queryFn: async () => {
      const stories = await api.listStories();
      const basicStory = stories.data.find((s: any) => s.id === storyId);
      if (!basicStory) return null;
      return api.getStory(basicStory.slug);
    },
    enabled: !!storyId,
  });

  // Get full story audio with selected language
  const { data: audioData, isLoading: audioLoading } = useQuery({
    queryKey: ['full-story-audio', storyId, selectedLanguage],
    queryFn: () => {
      if (!storyId) return null;
      return api.getFullStoryAudio(storyId, selectedLanguage);
    },
    enabled: !!storyId,
  });

  const handleLanguageChange = (langCode: string) => {
    setSelectedLanguage(langCode);
    // Pause current audio if playing
    if (audioElement) {
      audioElement.pause();
      setPlaying(null);
    }
  };

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

        {/* Language Selector */}
        <Card className="max-w-2xl mx-auto mb-6">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Globe className="w-5 h-5" />
              <span className="font-medium">Select Language:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {LANGUAGES.filter(lang => story.available_languages?.includes(lang.code)).map((lang) => (
                <Button
                  key={lang.code}
                  variant={selectedLanguage === lang.code ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleLanguageChange(lang.code)}
                >
                  <span className="mr-2">{lang.flag}</span>
                  {lang.name}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {audioLoading ? (
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Generating audio in {LANGUAGES.find(l => l.code === selectedLanguage)?.name}...</p>
          </div>
        ) : audioData?.audio_url ? (
          <Card className="max-w-2xl mx-auto">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <Button
                  size="lg"
                  onClick={() => playAudio(audioData.audio_url, 'full-story')}
                >
                  {playing === 'full-story' ? (
                    <Pause className="w-5 h-5 mr-2" />
                  ) : (
                    <Play className="w-5 h-5 mr-2" />
                  )}
                  {playing === 'full-story' ? 'Pause' : 'Play Full Story'}
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
                <p>Language: {LANGUAGES.find(l => l.code === selectedLanguage)?.name}</p>
                <p>Total Nodes: {audioData.total_nodes}</p>
                <p>Duration: {Math.round(audioData.total_duration_sec)} seconds</p>
                <p>File Size: {((audioData.file_size || 0) / 1024).toFixed(1)} KB</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="text-center">
            <p className="text-muted-foreground">Audio not available for this language</p>
          </div>
        )}
      </div>
    </div>
  );
}
