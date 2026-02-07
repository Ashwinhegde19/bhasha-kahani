'use client';

import { useMutation } from '@tanstack/react-query';
import { useUserStore } from '@/store';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export function useAuth() {
  const { setUser, clearUser, user, token, isAuthenticated } = useUserStore();

  const anonymousAuth = useMutation({
    mutationFn: api.anonymousAuth,
    onSuccess: (data) => {
      setUser(
        {
          id: data.user_id,
          anonymous_id: `anon_${data.user_id}`,
          created_at: new Date().toISOString(),
          last_active: new Date().toISOString(),
          preferences: {
            language: 'en',
            code_mix_ratio: 0.3,
            volume: 0.8,
            autoPlay: true,
          },
        },
        data.access_token
      );
      toast.success('Welcome to Bhasha Kahani!');
    },
    onError: () => {
      toast.error('Failed to initialize. Please try again.');
    },
  });

  const logout = () => {
    clearUser();
    api.clearToken();
    toast.success('Logged out successfully');
  };

  return {
    user,
    token,
    isAuthenticated,
    anonymousAuth,
    logout,
  };
}
