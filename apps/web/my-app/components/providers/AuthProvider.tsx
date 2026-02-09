'use client';

import { useEffect, useRef } from 'react';
import { useUserStore } from '@/store';
import { api } from '@/lib/api';
import { User } from '@/types';

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { token, language, setUser, clearUser } = useUserStore();
  const hasBootstrappedRef = useRef(false);

  useEffect(() => {
    // Set token in API client whenever it changes
    if (token) {
      api.setToken(token);
      return;
    }

    api.clearToken();
    if (hasBootstrappedRef.current) return;
    hasBootstrappedRef.current = true;

    let cancelled = false;

    const bootstrapAnonymousUser = async () => {
      try {
        const auth = await api.anonymousAuth();
        if (cancelled) return;

        const now = new Date().toISOString();
        const anonymousUser: User = {
          id: auth.user_id,
          anonymous_id: `anon_${auth.user_id.slice(0, 8)}`,
          created_at: now,
          last_active: now,
          preferences: {
            language,
            code_mix_ratio: 0,
            volume: 1,
            autoPlay: true,
          },
        };

        setUser(anonymousUser, auth.access_token);
        api.setToken(auth.access_token);
      } catch {
        if (cancelled) return;
        hasBootstrappedRef.current = false;
        clearUser();
        api.clearToken();
      }
    };

    void bootstrapAnonymousUser();

    return () => {
      cancelled = true;
    };
  }, [token, language, setUser, clearUser]);

  return <>{children}</>;
}
