'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { crmApi } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    crmApi.getSessionStatus()
      .then(({ authenticated }) => router.replace(authenticated ? '/dashboard' : '/login'))
      .catch(() => router.replace('/login'));
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="flex items-center gap-3 text-slate-500 text-sm">
        <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <span>Loading NexusCRM...</span>
      </div>
    </div>
  );
}
