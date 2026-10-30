'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Shield, Users, Building2, Key, Plus, CheckCircle2 } from 'lucide-react';
import { User } from '@/types/crm';
import { getOrganizationDisplayName } from '@/lib/brand';

export default function SettingsPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('crm_user');
      if (stored) {
        try {
          setCurrentUser(JSON.parse(stored));
        } catch (e) {}
      } else {
        setCurrentUser({
          id: 1,
          full_name: 'Sarah Jenkins',
          email: 'admin@crm.io',
          role: 'ADMIN',
          organization_id: 1,
          organization_name: 'NexusCRM Enterprise',
          is_active: true,
          is_superuser: true,
        });
      }
    }
  }, []);

  const teamRoster = [
    { name: 'Sarah Jenkins', email: 'admin@crm.io', role: 'ADMIN', status: 'Active' },
    { name: 'Alex Rivera', email: 'alex.sales@crm.io', role: 'SALES_REP', status: 'Active' },
    { name: 'Marcus Vance', email: 'm.vance@apexhealth.org', role: 'VIEWER', status: 'Active' },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Organization & Security Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Tenant isolation, role-based access controls, and organization membership configuration
        </p>
      </div>

      {/* Organization Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-bold">
            <Building2 size={20} />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm">{getOrganizationDisplayName(currentUser?.organization_name)}</h3>
            <span className="text-[11px] text-slate-400 font-mono">Tenant ID: org_001 &bull; Plan: ENTERPRISE TIER</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-slate-100 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Security Model</span>
            <span className="font-semibold text-emerald-600 flex items-center gap-1 mt-0.5">
              <Shield size={12} />
              Logical DB Isolation
            </span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Session Security</span>
            <span className="font-semibold text-slate-800 mt-0.5 block">HTTP-Only JWT Token</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Audit Logging</span>
            <span className="font-semibold text-slate-800 mt-0.5 block">Enabled (PostgreSQL)</span>
          </div>
        </div>
      </div>

      {/* Team Roster */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Team Members & Role-Based Permissions</h3>
            <p className="text-xs text-slate-500">Admins have full access, Sales Reps manage permitted records, Viewers are read-only</p>
          </div>
          <button
            onClick={() => alert('Invite member modal')}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs"
          >
            <Plus size={14} />
            Invite Member
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="pb-2">User</th>
                <th className="pb-2">Email</th>
                <th className="pb-2">Role</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {teamRoster.map((u, i) => (
                <tr key={i} className="hover:bg-slate-50/60">
                  <td className="py-2.5 font-semibold text-slate-900">{u.name}</td>
                  <td className="py-2.5 text-slate-600">{u.email}</td>
                  <td className="py-2.5">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        u.role === 'ADMIN'
                          ? 'bg-purple-50 text-purple-700 border border-purple-200'
                          : u.role === 'SALES_REP'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {u.role}
                    </span>
                  </td>
                  <td className="py-2.5 text-emerald-600 font-semibold">{u.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
