'use client';

import { cn } from '@/lib/utils';
import { BookOpen } from 'lucide-react';

/* ============================================
   Floating Decorative Elements
   ============================================ */

interface FloatingElementProps {
  className?: string;
  size?: number;
  delay?: string;
}

export function FloatingStar({ className, size = 16, delay = '0s' }: FloatingElementProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={cn('animate-float text-amber-400/60 dark:text-amber-300/40', className)}
      style={{ animationDelay: delay }}
      aria-hidden="true"
    >
      <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 16.8l-6.2 4.5 2.4-7.4L2 9.4h7.6z" />
    </svg>
  );
}

export function FloatingSparkle({ className, size = 12, delay = '0s' }: FloatingElementProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={cn('animate-twinkle text-primary/50', className)}
      style={{ animationDelay: delay }}
      aria-hidden="true"
    >
      <path d="M12 0L14 10L24 12L14 14L12 24L10 14L0 12L10 10Z" />
    </svg>
  );
}

export function FloatingBook({ className, size = 24, delay = '0s' }: FloatingElementProps) {
  return (
    <div
      className={cn('animate-float-rotate text-primary/30', className)}
      style={{ animationDelay: delay }}
      aria-hidden="true"
    >
      <BookOpen size={size} />
    </div>
  );
}

/* ============================================
   Floating Cloud
   ============================================ */

export function FloatingCloud({ className, size = 48, delay = '0s' }: FloatingElementProps) {
  return (
    <svg
      width={size}
      height={size * 0.6}
      viewBox="0 0 80 48"
      fill="currentColor"
      className={cn('animate-float text-primary/10', className)}
      style={{ animationDelay: delay, animationDuration: '5s' }}
      aria-hidden="true"
    >
      <ellipse cx="30" cy="32" rx="28" ry="14" />
      <ellipse cx="50" cy="28" rx="22" ry="16" />
      <ellipse cx="22" cy="26" rx="18" ry="12" />
      <ellipse cx="40" cy="20" rx="16" ry="14" />
    </svg>
  );
}

/* ============================================
   Section Dividers
   ============================================ */

interface WaveDividerProps {
  className?: string;
  flip?: boolean;
}

export function WaveDivider({ className, flip = false }: WaveDividerProps) {
  return (
    <div
      className={cn('w-full overflow-hidden leading-none', flip && 'rotate-180', className)}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 1440 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-auto"
        preserveAspectRatio="none"
      >
        <path
          d="M0 60C240 120 480 0 720 60C960 120 1200 0 1440 60V120H0V60Z"
          className="fill-background"
        />
      </svg>
    </div>
  );
}

/* ============================================
   Decorative Card Corners
   ============================================ */

interface DecorativeCornerProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  className?: string;
}

const CORNER_POSITIONS: Record<string, string> = {
  'top-left': 'top-0 left-0',
  'top-right': 'top-0 right-0',
  'bottom-left': 'bottom-0 left-0',
  'bottom-right': 'bottom-0 right-0',
};

const CORNER_TRANSFORMS: Record<string, string> = {
  'top-left': '',
  'top-right': 'scale-x-[-1]',
  'bottom-left': 'scale-y-[-1]',
  'bottom-right': 'scale-[-1]',
};

export function DecorativeCorner({ position, className }: DecorativeCornerProps) {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      className={cn(
        'absolute text-primary/20 pointer-events-none',
        CORNER_POSITIONS[position],
        CORNER_TRANSFORMS[position],
        className,
      )}
      aria-hidden="true"
    >
      <path
        d="M0 0C0 0 8 0 16 8C24 16 32 32 32 32"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
      />
      <circle cx="4" cy="4" r="2" fill="currentColor" />
    </svg>
  );
}

/* ============================================
   Illustrated Card Fallback SVGs
   ============================================ */

const SCENE_COLORS = [
  { sky: '#FEF3C7', ground: '#FDE68A', accent: '#F59E0B', detail: '#D97706' },
  { sky: '#FCE7F3', ground: '#FBCFE8', accent: '#EC4899', detail: '#BE185D' },
  { sky: '#E0F2FE', ground: '#BAE6FD', accent: '#0EA5E9', detail: '#0369A1' },
  { sky: '#D1FAE5', ground: '#A7F3D0', accent: '#10B981', detail: '#047857' },
  { sky: '#EDE9FE', ground: '#DDD6FE', accent: '#8B5CF6', detail: '#6D28D9' },
  { sky: '#FFF7ED', ground: '#FED7AA', accent: '#F97316', detail: '#C2410C' },
];

export function IllustratedScene({ index = 0, className }: { index?: number; className?: string }) {
  const c = SCENE_COLORS[index % SCENE_COLORS.length];
  return (
    <svg viewBox="0 0 400 300" fill="none" className={cn('w-full h-full', className)} aria-hidden="true">
      {/* Sky */}
      <rect width="400" height="300" fill={c.sky} />
      {/* Sun */}
      <circle cx="320" cy="70" r="35" fill={c.accent} opacity="0.8">
        <animate attributeName="r" values="35;38;35" dur="3s" repeatCount="indefinite" />
      </circle>
      {/* Sun rays */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
        <line
          key={angle}
          x1="320"
          y1="70"
          x2={320 + Math.cos((angle * Math.PI) / 180) * 52}
          y2={70 + Math.sin((angle * Math.PI) / 180) * 52}
          stroke={c.accent}
          strokeWidth="2"
          opacity="0.4"
        >
          <animate attributeName="opacity" values="0.4;0.7;0.4" dur="2s" begin={`${angle * 0.01}s`} repeatCount="indefinite" />
        </line>
      ))}
      {/* Clouds */}
      <g opacity="0.6">
        <ellipse cx="90" cy="60" rx="35" ry="16" fill="white">
          <animate attributeName="cx" values="90;110;90" dur="8s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="110" cy="55" rx="28" ry="18" fill="white">
          <animate attributeName="cx" values="110;130;110" dur="8s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="200" cy="45" rx="25" ry="12" fill="white">
          <animate attributeName="cx" values="200;215;200" dur="10s" repeatCount="indefinite" />
        </ellipse>
      </g>
      {/* Rolling hills */}
      <ellipse cx="100" cy="280" rx="180" ry="80" fill={c.ground} />
      <ellipse cx="320" cy="290" rx="160" ry="70" fill={c.accent} opacity="0.3" />
      {/* Trees */}
      <g>
        <rect x="145" y="195" width="8" height="40" rx="3" fill={c.detail} />
        <circle cx="149" cy="185" r="22" fill={c.accent} opacity="0.8">
          <animate attributeName="r" values="22;24;22" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="140" cy="192" r="15" fill={c.accent} opacity="0.6" />
      </g>
      <g>
        <rect x="255" y="210" width="6" height="30" rx="3" fill={c.detail} />
        <circle cx="258" cy="202" r="16" fill={c.accent} opacity="0.7">
          <animate attributeName="r" values="16;18;16" dur="3.5s" repeatCount="indefinite" />
        </circle>
      </g>
      {/* Birds */}
      <g opacity="0.5">
        <path d="M180 100 Q185 94 190 100" stroke={c.detail} strokeWidth="2" fill="none">
          <animate attributeName="d" values="M180 100 Q185 94 190 100;M180 98 Q185 92 190 98;M180 100 Q185 94 190 100" dur="1.5s" repeatCount="indefinite" />
        </path>
        <path d="M210 85 Q215 79 220 85" stroke={c.detail} strokeWidth="2" fill="none">
          <animate attributeName="d" values="M210 85 Q215 79 220 85;M210 83 Q215 77 220 83;M210 85 Q215 79 220 85" dur="1.8s" repeatCount="indefinite" />
        </path>
        <path d="M240 95 Q245 89 250 95" stroke={c.detail} strokeWidth="2" fill="none">
          <animate attributeName="d" values="M240 95 Q245 89 250 95;M240 93 Q245 87 250 93;M240 95 Q245 89 250 95" dur="1.3s" repeatCount="indefinite" />
        </path>
      </g>
      {/* Animated flowers */}
      <g>
        <circle cx="80" cy="245" r="5" fill={c.accent}>
          <animate attributeName="r" values="5;6;5" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="200" cy="258" r="4" fill={c.detail} opacity="0.7">
          <animate attributeName="r" values="4;5;4" dur="2.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="300" cy="250" r="4.5" fill={c.accent} opacity="0.6">
          <animate attributeName="r" values="4.5;5.5;4.5" dur="3s" repeatCount="indefinite" />
        </circle>
      </g>
      {/* Sparkle star */}
      <g opacity="0.5">
        <path d="M60 130 L62 136 L68 136 L63 140 L65 146 L60 142 L55 146 L57 140 L52 136 L58 136Z" fill={c.accent}>
          <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />
        </path>
      </g>
    </svg>
  );
}

/* ============================================
   Background Particle System
   ============================================ */

export function BackgroundParticles({ className }: { className?: string }) {
  return (
    <div className={cn('fixed inset-0 overflow-hidden pointer-events-none z-0', className)} aria-hidden="true">
      {/* Drifting stars */}
      <FloatingStar className="absolute top-[8%] animate-drift-right text-amber-300/30" size={16} delay="0s" />
      <FloatingStar className="absolute top-[25%] animate-drift-left text-rose-300/25" size={12} delay="3s" />
      <FloatingStar className="absolute top-[55%] animate-drift-right text-violet-300/20" size={10} delay="7s" />
      <FloatingStar className="absolute top-[75%] animate-drift-left text-amber-300/25" size={14} delay="5s" />
      {/* Drifting sparkles */}
      <FloatingSparkle className="absolute top-[15%] animate-drift-left text-primary/20" size={10} delay="2s" />
      <FloatingSparkle className="absolute top-[45%] animate-drift-right text-rose-400/20" size={8} delay="9s" />
      <FloatingSparkle className="absolute top-[85%] animate-drift-left text-sky-300/20" size={12} delay="4s" />
      {/* Floating clouds */}
      <FloatingCloud className="absolute top-[5%] left-[10%] text-primary/5" size={80} delay="0s" />
      <FloatingCloud className="absolute top-[30%] right-[5%] text-rose-400/5" size={60} delay="2s" />
    </div>
  );
}

/* ============================================
   Pre-composed Sparkle Group (for hero sections)
   — denser, more elements, bigger motion
   ============================================ */

interface SparkleGroupProps {
  className?: string;
  dense?: boolean;
}

export function SparkleGroup({ className, dense = false }: SparkleGroupProps) {
  return (
    <div
      className={cn('absolute inset-0 overflow-hidden pointer-events-none', className)}
      aria-hidden="true"
    >
      <FloatingStar className="absolute top-[10%] left-[5%]" size={22} delay="0s" />
      <FloatingSparkle className="absolute top-[15%] right-[10%]" size={16} delay="0.5s" />
      <FloatingStar className="absolute top-[40%] right-[5%]" size={16} delay="1s" />
      <FloatingSparkle className="absolute bottom-[20%] left-[8%]" size={12} delay="1.5s" />
      <FloatingBook className="absolute top-[25%] left-[85%]" size={30} delay="0.8s" />
      <FloatingSparkle className="absolute bottom-[30%] right-[15%]" size={18} delay="0.3s" />
      <FloatingStar className="absolute bottom-[10%] left-[50%]" size={14} delay="2s" />
      <FloatingCloud className="absolute top-[5%] left-[20%] text-primary/8" size={70} delay="0s" />
      <FloatingCloud className="absolute top-[60%] right-[10%] text-rose-400/6" size={55} delay="3s" />
      {dense && (
        <>
          <FloatingStar className="absolute top-[30%] left-[30%]" size={10} delay="0.7s" />
          <FloatingSparkle className="absolute top-[50%] left-[60%]" size={14} delay="1.2s" />
          <FloatingStar className="absolute top-[70%] right-[30%]" size={12} delay="1.8s" />
          <FloatingBook className="absolute bottom-[15%] left-[20%]" size={22} delay="2.2s" />
          <FloatingSparkle className="absolute top-[5%] left-[50%]" size={10} delay="0.2s" />
          <FloatingStar className="absolute bottom-[40%] left-[45%]" size={18} delay="2.5s" />
        </>
      )}
    </div>
  );
}
