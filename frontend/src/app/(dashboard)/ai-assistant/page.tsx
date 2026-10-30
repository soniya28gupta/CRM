'use client';

import React from 'react';
import { Bot, Sparkles, ShieldCheck, Database, Zap } from 'lucide-react';
import { AIChatPanel } from '@/components/ai/AIChatPanel';

export default function AIAssistantPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI CRM Copilot & Natural Language Query</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 font-bold border border-purple-200">
              Backend Secure Tool Execution
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Ask complex queries across your authorized leads, pipelines, meetings, and revenue analytics
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <ShieldCheck size={16} className="text-emerald-500" />
            <span>Strict RBAC Enforced</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Database size={16} className="text-blue-500" />
            <span>PostgreSQL Tools</span>
          </div>
        </div>
      </div>

      {/* Main Chat Panel */}
      <AIChatPanel />
    </div>
  );
}

