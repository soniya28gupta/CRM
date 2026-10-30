'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Users, UserCheck, Building2,
  Kanban, Calendar, CheckSquare, Clock,
  Bot, Layers, BarChart3, Settings, ChevronLeft,
  ChevronRight, Sparkles, PhoneCall, Shield
} from 'lucide-react';

interface SidebarProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: Users, badge: 'AI Scored' },
  { name: 'Contacts', href: '/contacts', icon: UserCheck },
  { name: 'Accounts', href: '/accounts', icon: Building2 },
  { name: 'Deals & Pipeline', href: '/deals', icon: Kanban },
  { name: 'Activities', href: '/activities', icon: Clock },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Meetings', href: '/meetings', icon: Calendar },
  { name: 'AI Assistant', href: '/ai-assistant', icon: Bot, highlight: true },
  { name: 'Industry Modules', href: '/industry-modules', icon: Layers },
  { name: 'Reports & Analytics', href: '/reports', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = () => {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={`fixed top-0 left-0 z-30 h-screen transition-all duration-300 bg-crm-navy border-r border-slate-800 text-slate-300 flex flex-col justify-between ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800 bg-slate-950/40">
          {!isCollapsed && (
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-500/20">
                N
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-white text-base tracking-tight leading-tight">NexusCRM</span>
                <span className="text-[10px] text-blue-400 font-medium tracking-wide uppercase">AI-Powered CRM</span>
              </div>
            </Link>
          )}

          {isCollapsed && (
            <Link href="/dashboard" className="mx-auto">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
                N
              </div>
            </Link>
          )}

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all group relative ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                    : item.highlight
                    ? 'text-blue-400 hover:bg-slate-800/80 hover:text-blue-300'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <Icon size={19} className={`shrink-0 ${isActive ? 'text-white' : item.highlight ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'}`} />

                {!isCollapsed && (
                  <span className="truncate flex-1">{item.name}</span>
                )}

                {!isCollapsed && item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 font-semibold border border-blue-500/30">
                    {item.badge}
                  </span>
                )}

                {/* Collapsed Tooltip */}
                {isCollapsed && (
                  <div className="absolute left-full ml-3 px-2.5 py-1 bg-slate-900 text-white text-xs rounded-md shadow-lg border border-slate-700 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-50 transition-opacity">
                    {item.name}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Organization Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/30">
        {!isCollapsed ? (
          <div className="flex items-center gap-2.5 px-2 py-1.5 text-xs text-slate-400">
            <Shield size={16} className="text-emerald-400 shrink-0" />
            <div className="flex flex-col truncate">
              <span className="font-medium text-slate-200 truncate">NexusCRM Enterprise</span>
              <span className="text-[10px] text-emerald-400">Tenant Isolated • Active</span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center py-1">
            <Shield size={18} className="text-emerald-400" />
          </div>
        )}
      </div>
    </aside>
  );
};
