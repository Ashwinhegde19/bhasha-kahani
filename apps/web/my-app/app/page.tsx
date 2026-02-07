'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, ChevronRight, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';
import { cn } from '@/lib/utils';

export default function HomePage() {
  const router = useRouter();
  const { user, updatePreferences } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState(user?.preferences.language || 'en');

  const handleLanguageSelect = (languageCode: string) => {
    setSelectedLanguage(languageCode);
    updatePreferences({ language: languageCode });
  };

  const handleStartExploring = () => {
    router.push('/stories');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-6">
            <BookOpen className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
            Bhasha Kahani
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Discover interactive folktales in multiple Indian languages. 
            Listen, choose your path, and experience stories like never before.
          </p>
        </div>

        {/* Language Selection */}
        <div className="max-w-3xl mx-auto mb-12">
          <div className="flex items-center justify-center gap-2 mb-6">
            <Globe className="w-5 h-5 text-muted-foreground" />
            <h2 className="text-lg font-medium">Select your language</h2>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {LANGUAGES.map((lang) => (
              <Card
                key={lang.code}
                className={cn(
                  'cursor-pointer transition-all hover:shadow-md',
                  selectedLanguage === lang.code 
                    ? 'border-primary bg-primary/5' 
                    : 'hover:border-muted-foreground/20'
                )}
                onClick={() => handleLanguageSelect(lang.code)}
              >
                <CardContent className="p-4 text-center">
                  <span className="text-2xl mb-2 block">{lang.flag}</span>
                  <span className="font-medium">{lang.name}</span>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Button */}
        <div className="text-center">
          <Button 
            size="lg" 
            className="px-8 py-6 text-lg"
            onClick={handleStartExploring}
          >
            Start Exploring Stories
            <ChevronRight className="ml-2 w-5 h-5" />
          </Button>
          <p className="mt-4 text-sm text-muted-foreground">
            No account required. Start listening immediately.
          </p>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16 border-t">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🎧</span>
            </div>
            <h3 className="font-semibold mb-2">Audio Stories</h3>
            <p className="text-muted-foreground">
              Listen to stories in your preferred language with high-quality audio
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="font-semibold mb-2">Interactive Choices</h3>
            <p className="text-muted-foreground">
              Make decisions that shape the story outcome
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🌍</span>
            </div>
            <h3 className="font-semibold mb-2">Multiple Languages</h3>
            <p className="text-muted-foreground">
              Stories available in Hindi, Bengali, Tamil, and more
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
