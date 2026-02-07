import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AudioState {
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setPlaybackRate: (rate: number) => void;
}

export const useAudioStore = create<AudioState>()(
  persist(
    (set, get) => ({
      volume: 0.8,
      isMuted: false,
      playbackRate: 1,
      setVolume: (volume) => set({ volume: Math.max(0, Math.min(1, volume)) }),
      toggleMute: () => set({ isMuted: !get().isMuted }),
      setPlaybackRate: (rate) => set({ playbackRate: rate }),
    }),
    {
      name: 'audio-storage',
    }
  )
);
