'use client';

import { UserProvider } from '@/context/UserContext';
import React, { ReactNode } from 'react';

export default function ClientProviders({ children }: { children: ReactNode }) {
  return (
    <UserProvider>
      {children}
    </UserProvider>
  );
}