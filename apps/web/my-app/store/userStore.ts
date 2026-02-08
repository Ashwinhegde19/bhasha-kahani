import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserPreferences } from '@/types';

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  language: string; // Persisted independently for anonymous users
  setUser: (user: User, token: string) => void;
  clearUser: () => void;
  setLanguage: (language: string) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      language: 'en',
      setUser: (user, token) => {
        set({ user, token, isAuthenticated: true });
      },
      clearUser: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
      setLanguage: (language) => {
        set({ language });
        // Also update user preferences if logged in
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: {
              ...currentUser,
              preferences: {
                ...currentUser.preferences,
                language,
              },
            },
          });
        }
      },
      updatePreferences: (preferences) => {
        // Update language at top level if provided
        if (preferences.language) {
          set({ language: preferences.language });
        }
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: {
              ...currentUser,
              preferences: {
                ...currentUser.preferences,
                ...preferences,
              },
            },
          });
        }
      },
    }),
    {
      name: 'user-storage',
    }
  )
);
