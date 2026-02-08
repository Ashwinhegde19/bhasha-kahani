'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronRight, Globe, Headphones, Languages, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';
import { cn } from '@/lib/utils';

export function HomeContent() {
  const router = useRouter();
  const { language: storedLanguage, setLanguage } = useUserStore();
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [isHydrated, setIsHydrated] = useState(false);

  // Ensure component is hydrated before rendering
  useEffect(() => {
    setSelectedLanguage(storedLanguage || 'en');
    setIsHydrated(true);
  }, [storedLanguage]);

  const handleLanguageSelect = (languageCode: string) => {
    setSelectedLanguage(languageCode);
    setLanguage(languageCode);
  };

  const handleStartExploring = () => {
    router.push('/stories');
  };

  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-orange-50/50 to-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-12 pb-8 md:pt-20 md:pb-12">
        <div className="text-center mb-10">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-4">
            Bhasha Kahani
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Interactive folktales for children in English, Hindi, and Kannada.
            Listen and experience stories like never before.
          </p>
        </div>

        {/* Language Selection */}
        <div className="max-w-md mx-auto mb-10">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-muted-foreground" />
            <h2 className="text-lg font-medium">Pick your language</h2>
          </div>
          
          <div className="grid grid-cols-3 gap-3">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                className={cn(
                  'rounded-xl py-4 px-3 text-center transition-all cursor-pointer',
                  'border-2 hover:shadow-md',
                  selectedLanguage === lang.code
                    ? 'border-primary bg-primary/10 shadow-md'
                    : 'border-transparent bg-white/70 hover:border-primary/30'
                )}
                onClick={() => handleLanguageSelect(lang.code)}
              >
                <span className="text-3xl block mb-1">{lang.flag}</span>
                <span className="font-semibold text-base">{lang.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* CTA Button */}
        <div className="text-center">
          <Button 
            size="lg" 
            className="px-10 py-7 text-xl rounded-full shadow-lg hover:shadow-xl transition-all animate-gentle-bounce"
            onClick={handleStartExploring}
          >
            Start Exploring
            <ChevronRight className="ml-1 w-6 h-6" />
          </Button>
          <p className="mt-4 text-sm text-muted-foreground">
            No account needed. Start listening right away.
          </p>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          {[
            {
              icon: Headphones,
              title: 'Audio Stories',
              desc: 'High-quality voices powered by Sarvam AI bring every character to life',
              color: 'bg-amber-100 text-amber-600',
            },
            {
              icon: Sparkles,
              title: 'Character Voices',
              desc: 'Each character has their own unique voice for an immersive experience',
              color: 'bg-rose-100 text-rose-600',
            },
            {
              icon: Languages,
              title: 'Multiple Languages',
              desc: 'Switch between English, Hindi, and Kannada at any time',
              color: 'bg-sky-100 text-sky-600',
            },
          ].map((feature) => (
            <div key={feature.title} className="text-center bg-white/60 rounded-2xl p-6">
              <div className={cn('w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4', feature.color)}>
                <feature.icon className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
