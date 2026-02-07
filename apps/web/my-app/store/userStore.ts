import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserPreferences } from '@/types';

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User, token: string) => void;
  clearUser: () => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setUser: (user, token) => {
        set({ user, token, isAuthenticated: true });
      },
      clearUser: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
      updatePreferences: (preferences) => {
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
