'use client';

import { useRouter } from 'next/navigation';
import { ChevronRight, Globe, Headphones, Languages, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUserStore } from '@/store';
import { LANGUAGES } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { SparkleGroup, WaveDivider, FloatingSparkle, BackgroundParticles } from '@/components/ui/decorative';

const FEATURES = [
  {
    icon: Headphones,
    title: 'Audio Stories',
    desc: 'High-quality voices powered by Sarvam AI bring every character to life',
    gradient: 'from-amber-400 to-orange-500',
  },
  {
    icon: Sparkles,
    title: 'Character Voices',
    desc: 'Each character has their own unique voice for an immersive experience',
    gradient: 'from-rose-400 to-pink-500',
  },
  {
    icon: Languages,
    title: 'Multiple Languages',
    desc: 'Switch between English, Hindi, and Kannada at any time',
    gradient: 'from-sky-400 to-cyan-500',
  },
];

export function HomeContent() {
  const router = useRouter();
  const { language: selectedLanguage, setLanguage } = useUserStore();

  const handleLanguageSelect = (languageCode: string) => {
    setLanguage(languageCode);
  };

  const handleStartExploring = () => {
    router.push('/stories');
  };

  return (
    <div className="min-h-screen relative">
      <BackgroundParticles />

      {/* Hero Section */}
      <div className="relative bg-gradient-to-b from-amber-50 via-orange-50/50 to-background dark:from-background dark:via-background dark:to-background overflow-hidden">
        <SparkleGroup dense />

        <div className="container mx-auto px-4 pt-16 pb-12 md:pt-24 md:pb-16 relative z-10">
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-semibold tracking-tight mb-6 gradient-text animate-pop-in">
              Bhasha Kahani
            </h1>

            {/* Decorative sparkle divider */}
            <div className="flex items-center justify-center gap-3 mb-6 animate-scale-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="h-px w-16 bg-gradient-to-r from-transparent to-primary/40" />
              <FloatingSparkle size={16} className="text-primary/60" delay="0s" />
              <div className="h-px w-16 bg-gradient-to-l from-transparent to-primary/40" />
            </div>

            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed animate-slide-in-up" style={{ animationDelay: '0.3s' }}>
              Interactive folktales for children in English, Hindi, and Kannada.
              Listen and experience stories like never before.
            </p>
          </div>

          {/* Language Selection */}
          <div className="max-w-lg mx-auto mb-12 animate-slide-in-up" style={{ animationDelay: '0.4s' }}>
            <div className="flex items-center justify-center gap-2 mb-5">
              <Globe className="w-5 h-5 text-primary/70 animate-slow-spin" />
              <h2 className="text-lg font-semibold">Pick your language</h2>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {LANGUAGES.map((lang, i) => (
                <button
                  key={lang.code}
                  className={cn(
                    'rounded-2xl py-6 px-4 text-center transition-all cursor-pointer relative overflow-hidden hover-jelly',
                    'border-2 hover:shadow-lg hover:-translate-y-1',
                    'animate-pop-in',
                    selectedLanguage === lang.code
                      ? 'border-primary bg-gradient-to-br from-primary/15 to-primary/5 shadow-lg'
                      : 'border-border/30 bg-card/70 dark:bg-secondary/50 hover:border-primary/30',
                  )}
                  style={{ animationDelay: `${0.5 + i * 0.1}s` }}
                  onClick={() => handleLanguageSelect(lang.code)}
                >
                  <span className="text-5xl block mb-2">{lang.flag}</span>
                  <span className="font-semibold text-lg block">{lang.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* CTA Button */}
          <div className="text-center animate-slide-in-up" style={{ animationDelay: '0.6s' }}>
            <Button
              size="lg"
              className="sparkle-button px-10 py-7 text-xl rounded-full shadow-lg hover:shadow-xl transition-all animate-heartbeat bg-gradient-to-r from-primary to-rose-500 hover:from-primary/90 hover:to-rose-500/90 text-white border-0 animate-gradient"
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

        <WaveDivider className="-mb-1" />
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-semibold gradient-text mb-2">
            A Magical Experience
          </h2>
          <p className="text-muted-foreground">Stories come alive with voice, character, and language</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          {FEATURES.map((feature, i) => (
            <div
              key={feature.title}
              className="text-center glass-card rounded-2xl p-6 hover:shadow-lg transition-all hover:-translate-y-2 hover-wiggle animate-slide-in-up"
              style={{ animationDelay: `${i * 0.15}s` }}
            >
              <div
                className={cn(
                  'w-16 h-16 rounded-2xl bg-gradient-to-br flex items-center justify-center mx-auto mb-4 shadow-md animate-bounce-rotate',
                  feature.gradient,
                )}
                style={{ animationDelay: `${0.3 + i * 0.15}s` }}
              >
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
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
