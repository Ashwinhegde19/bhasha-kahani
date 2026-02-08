'use client';

import { useEffect } from 'react';
import { useUserStore } from '@/store';
import { api } from '@/lib/api';

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { token, user } = useUserStore();

  useEffect(() => {
    // Set token in API client whenever it changes
    if (token) {
      api.setToken(token);
    } else {
      api.clearToken();
    }
  }, [token]);

  return <>{children}</>;
}
