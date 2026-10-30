'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { Topbar } from '@/components/layout/Topbar';
import { LeadModal } from '@/components/leads/LeadModal';
import { crmApi } from '@/lib/api';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [quickCreateType, setQuickCreateType] = useState<'lead' | 'contact' | 'deal' | 'task' | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [sessionError, setSessionError] = useState('');

  useEffect(() => {
    let active = true;
    crmApi.getSessionStatus()
      .then(({ authenticated }) => {
        if (!active) return;
        if (authenticated) {
          setAuthenticated(true);
        } else {
          router.replace('/login');
        }
      })
      .catch((error: unknown) => {
        if (!active) return;
        setSessionError(error instanceof Error ? error.message : 'Unable to verify your session.');
      });

    return () => {
      active = false;
    };
  }, [router]);

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        {sessionError ? (
          <div className="max-w-md p-6 text-center">
            <p className="text-sm text-red-700">{sessionError}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
            <span>Verifying your session...</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-w-0 transition-all duration-300">
        <Topbar onOpenQuickCreate={(type) => setQuickCreateType(type)} />
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* Quick Create Lead Modal */}
      {quickCreateType === 'lead' && (
        <LeadModal
          isOpen={true}
          onClose={() => setQuickCreateType(null)}
          onSuccess={() => {
            setQuickCreateType(null);
            if (typeof window !== 'undefined') window.location.reload();
          }}
        />
      )}
    </div>
  );
}
