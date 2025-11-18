'use client';

import { useEffect } from 'react';

interface ThemeEnforcerProps {
  theme: 'light' | 'dark';
}

export function ThemeEnforcer({ theme }: ThemeEnforcerProps) {
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }, [theme]);

  return null;
}
