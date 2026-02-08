'use client';

import { useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Volume2, Loader2, Globe, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';

export default function PlayStoryPage() {
  const params = useParams();
  const storyId = params.id as string;
  const [playing, setPlaying] = useState(false);
  const [currentNodeIndex, setCurrentNodeIndex] = useState(0);
  const [showChoices, setShowChoices] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const [choicesMade, setChoicesMade] = useState<{nodeId: string, choiceKey: string}[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Get user language preference
  const { user } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  
  // Update language when user data loads
  useEffect(() => {
    if (user?.preferences?.language) {
      setSelectedLanguage(user.preferences.language);
    }
  }, [user]);

  // Get story details
  const { data: story, isLoading: storyLoading } = useQuery({
    queryKey: ['story', storyId],
    queryFn: async () => {
      const stories = await api.listStories();
      const basicStory = stories.data.find((s: any) => s.id === storyId);
      if (!basicStory) return null;
      return api.getStory(basicStory.slug);
    },
    enabled: !!storyId,
  });

  // Get current node
  const narrationNodes = story?.nodes?.filter((n: any) => n.node_type === 'narration') || [];
  const choiceNodes = story?.nodes?.filter((n: any) => n.node_type === 'choice') || [];
  const currentNode = narrationNodes[currentNodeIndex];
  
  // Get audio for current node
  const { data: nodeAudio, isLoading: audioLoading } = useQuery({
    queryKey: ['node-audio', currentNode?.id, selectedLanguage],
    queryFn: () => {
      if (!currentNode?.id) return null;
      return api.getAudioUrl(currentNode.id, { 
        language: selectedLanguage,
        speaker: currentNode?.character?.bulbul_speaker || 'meera'
      });
    },
    enabled: !!currentNode?.id,
  });

  // Make choice mutation
  const makeChoiceMutation = useMutation({
    mutationFn: ({ nodeId, choiceKey }: { nodeId: string, choiceKey: string }) => {
      if (!story?.slug) throw new Error('Story not loaded');
      return api.makeChoice(story.slug, { node_id: nodeId, choice_key: choiceKey });
    },
    onSuccess: (data) => {
      // Find the next node index
      const nextNodeId = data.next_node?.id;
      const nextIndex = narrationNodes.findIndex((n: any) => n.id === nextNodeId);
      if (nextIndex !== -1) {
        setCurrentNodeIndex(nextIndex);
        setShowChoices(false);
      }
    },
  });

  const handleLanguageChange = (langCode: string) => {
    setSelectedLanguage(langCode);
    if (audioRef.current) {
      audioRef.current.pause();
      setPlaying(false);
    }
  };

  const playCurrentNode = () => {
    if (!nodeAudio?.audio_url) return;
    
    if (audioRef.current) {
      audioRef.current.pause();
    }

    const audio = new Audio(nodeAudio.audio_url);
    audio.onended = () => {
      setPlaying(false);
      // Check if next node is a choice
      const nextNode = narrationNodes[currentNodeIndex + 1];
      if (nextNode?.node_type === 'choice') {
        setShowChoices(true);
      } else if (currentNodeIndex < narrationNodes.length - 1) {
        setCurrentNodeIndex(prev => prev + 1);
      }
    };
    audio.play().catch(e => console.error('Audio play error:', e));
    audioRef.current = audio;
    setPlaying(true);
  };

  const handleChoice = (choiceKey: string) => {
    const currentChoiceNode = choiceNodes.find((n: any) => 
      narrationNodes[currentNodeIndex]?.display_order < n.display_order &&
      narrationNodes[currentNodeIndex + 1]?.display_order > n.display_order
    );
    
    if (currentChoiceNode) {
      setChoicesMade(prev => [...prev, { nodeId: currentChoiceNode.id, choiceKey }]);
      makeChoiceMutation.mutate({ nodeId: currentChoiceNode.id, choiceKey });
    }
  };

  const goToNextNode = () => {
    if (currentNodeIndex < narrationNodes.length - 1) {
      setCurrentNodeIndex(prev => prev + 1);
      setShowChoices(false);
    }
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
      {/* Header */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/stories/${story.slug}`}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Story
            </Link>
          </Button>
          
          {/* Language Selector */}
          <div className="flex gap-2">
            {LANGUAGES.filter(lang => story.available_languages?.includes(lang.code)).map((lang) => (
              <Button
                key={lang.code}
                variant={selectedLanguage === lang.code ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleLanguageChange(lang.code)}
              >
                <span className="mr-1">{lang.flag}</span>
                {lang.code.toUpperCase()}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="container mx-auto px-4 mb-4">
        <div className="w-full bg-muted rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all"
            style={{ width: `${((currentNodeIndex + 1) / narrationNodes.length) * 100}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-1 text-center">
          Part {currentNodeIndex + 1} of {narrationNodes.length}
        </p>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-4 max-w-3xl">
        {/* Character Avatar */}
        {currentNode?.character && (
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              {currentNode.character.avatar_url ? (
                <img 
                  src={currentNode.character.avatar_url} 
                  alt={currentNode.character.name}
                  className="w-10 h-10 rounded-full"
                />
              ) : (
                <Volume2 className="w-6 h-6 text-primary" />
              )}
            </div>
            <div>
              <p className="font-medium">{currentNode.character.name}</p>
              <p className="text-xs text-muted-foreground">
                {LANGUAGES.find(l => l.code === selectedLanguage)?.name}
              </p>
            </div>
          </div>
        )}

        {/* Story Text */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <p className="text-xl leading-relaxed">
              {(currentNode as any)?.text?.[selectedLanguage] || (currentNode as any)?.text?.['en'] || (currentNode as any)?.text_content?.[selectedLanguage] || (currentNode as any)?.text_content?.['en']}
            </p>
          </CardContent>
        </Card>

        {/* Audio Controls */}
        {audioLoading ? (
          <div className="text-center py-4">
            <Loader2 className="w-6 h-6 animate-spin mx-auto" />
            <p className="text-sm text-muted-foreground mt-2">Loading audio...</p>
          </div>
        ) : nodeAudio?.audio_url ? (
          <div className="flex justify-center gap-4 mb-6">
            <Button
              size="lg"
              onClick={playCurrentNode}
              disabled={playing}
            >
              {playing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Playing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Listen
                </>
              )}
            </Button>
            
            {!showChoices && currentNodeIndex < narrationNodes.length - 1 && (
              <Button
                variant="outline"
                size="lg"
                onClick={goToNextNode}
              >
                Skip
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
            )}
          </div>
        ) : null}

        {/* Choice Overlay */}
        {showChoices && (
          <Card className="border-2 border-primary">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-center">
                What happens next?
              </h3>
              <div className="space-y-3">
                {/* Get choices from the next choice node */}
                {(() => {
                  const nextChoiceNode = choiceNodes.find((n: any) => 
                    n.display_order > currentNode?.display_order
                  );
                  
                  return nextChoiceNode?.choices?.map((choice: any) => (
                    <Button
                      key={choice.choice_key}
                      variant="outline"
                      size="lg"
                      className="w-full justify-start text-left h-auto py-4"
                      onClick={() => handleChoice(choice.choice_key)}
                      disabled={makeChoiceMutation.isPending}
                    >
                      <span className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center mr-3 shrink-0">
                        {choice.choice_key}
                      </span>
                      <span>
                        {choice.text?.[selectedLanguage] || choice.text?.['en']}
                      </span>
                    </Button>
                  ));
                })()}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Story Complete */}
        {currentNodeIndex === narrationNodes.length - 1 && !showChoices && (
          <Card className="bg-green-50 border-green-200">
            <CardContent className="p-6 text-center">
              <h3 className="text-xl font-bold text-green-800 mb-2">
                🎉 Story Complete!
              </h3>
              <p className="text-green-700 mb-4">
                You finished "{story.title}" in {LANGUAGES.find(l => l.code === selectedLanguage)?.name}
              </p>
              <div className="flex justify-center gap-3">
                <Button onClick={() => {
                  setCurrentNodeIndex(0);
                  setChoicesMade([]);
                  setShowChoices(false);
                }}>
                  Play Again
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/stories">More Stories</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Debug Info */}
        <div className="mt-8 p-4 bg-muted rounded-lg text-xs text-muted-foreground">
          <p>Debug Info:</p>
          <p>Current Node: {currentNodeIndex + 1} / {narrationNodes.length}</p>
          <p>Node Type: {currentNode?.node_type}</p>
          <p>Character: {currentNode?.character?.name}</p>
          <p>Choices Made: {choicesMade.length}</p>
        </div>
      </div>
    </div>
  );
}
