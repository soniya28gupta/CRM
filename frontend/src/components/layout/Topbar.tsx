'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Search, Plus, Bell, Sparkles, User, LogOut,
  ChevronDown, CheckCircle, Clock, AlertTriangle, X
} from 'lucide-react';
import { crmApi } from '@/lib/api';
import { getOrganizationDisplayName } from '@/lib/brand';
import { GlobalSearchResult } from '@/types/crm';

interface TopbarProps {
  onOpenQuickCreate?: (type: 'lead' | 'contact' | 'deal' | 'task') => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onOpenQuickCreate }) => {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Record<string, GlobalSearchResult[]>>({});
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showCreateMenu, setShowCreateMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);

  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load local user session if present
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('crm_user');
      if (stored) {
        try {
          setCurrentUser(JSON.parse(stored));
        } catch (e) {}
      } else {
        // Default demo session
        setCurrentUser({
          full_name: 'Sarah Jenkins',
          email: 'admin@crm.io',
          role: 'ADMIN',
          organization_name: 'NexusCRM Enterprise'
        });
      }
    }

    // Keyboard shortcut CMD+K or / to focus search
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowSearchModal(true);
      }
      if (e.key === 'Escape') {
        setShowSearchModal(false);
        setShowCreateMenu(false);
        setShowProfileMenu(false);
        setShowNotifications(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults({});
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await crmApi.search(searchQuery.trim());
        setSearchResults(res);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleLogout = async () => {
    await crmApi.logout();
    router.push('/login');
  };

  const handleQuickAction = (type: 'lead' | 'contact' | 'deal' | 'task') => {
    setShowCreateMenu(false);
    if (onOpenQuickCreate) {
      onOpenQuickCreate(type);
    } else {
      router.push(`/${type === 'deal' ? 'deals' : type + 's'}?create=true`);
    }
  };

  return (
    <>
      <header className="h-16 bg-white border-b border-crm-bg-border sticky top-0 z-20 px-6 flex items-center justify-between shadow-sm">
        {/* Global Search Bar */}
        <div className="flex-1 max-w-xl">
          <button
            onClick={() => setShowSearchModal(true)}
            className="w-full flex items-center justify-between px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500 hover:bg-slate-100 hover:border-slate-300 transition-all group"
          >
            <div className="flex items-center gap-2.5">
              <Search size={16} className="text-slate-400 group-hover:text-blue-600 transition-colors" />
              <span>Search leads, deals, contacts, accounts...</span>
            </div>
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[11px] font-semibold text-slate-400 bg-white border border-slate-200 rounded shadow-xs">
              ⌘K
            </kbd>
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Quick Create Button */}
          <div className="relative">
            <button
              onClick={() => setShowCreateMenu(!showCreateMenu)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
            >
              <Plus size={16} />
              <span className="hidden sm:inline">Create</span>
              <ChevronDown size={14} className="opacity-80" />
            </button>

            {showCreateMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-lg py-1.5 z-40 text-sm">
                <button
                  onClick={() => handleQuickAction('lead')}
                  className="w-full text-left px-4 py-2 hover:bg-blue-50 text-slate-700 hover:text-blue-600 flex items-center gap-2.5"
                >
                  <span className="w-2 h-2 rounded-full bg-blue-500" />
                  New Lead
                </button>
                <button
                  onClick={() => handleQuickAction('contact')}
                  className="w-full text-left px-4 py-2 hover:bg-blue-50 text-slate-700 hover:text-blue-600 flex items-center gap-2.5"
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  New Contact
                </button>
                <button
                  onClick={() => handleQuickAction('deal')}
                  className="w-full text-left px-4 py-2 hover:bg-blue-50 text-slate-700 hover:text-blue-600 flex items-center gap-2.5"
                >
                  <span className="w-2 h-2 rounded-full bg-purple-500" />
                  New Deal
                </button>
                <button
                  onClick={() => handleQuickAction('task')}
                  className="w-full text-left px-4 py-2 hover:bg-blue-50 text-slate-700 hover:text-blue-600 flex items-center gap-2.5"
                >
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  New Task
                </button>
              </div>
            )}
          </div>

          {/* AI Assistant Quick Pill */}
          <Link
            href="/ai-assistant"
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg transition-colors"
          >
            <Sparkles size={14} className="text-purple-600" />
            <span className="hidden md:inline">Ask AI</span>
          </Link>

          {/* Notifications Popover */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg relative transition-colors"
            >
              <Bell size={18} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full" />
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-xl p-3 z-40 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
                  <span className="font-semibold text-slate-800 text-sm">Notifications</span>
                  <span className="text-[10px] text-blue-600 font-medium">3 unread</span>
                </div>
                <div className="space-y-2">
                  <div className="p-2 bg-blue-50/50 rounded-lg border border-blue-100 flex gap-2">
                    <CheckCircle size={15} className="text-blue-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-slate-800">Lead Converted to Won Deal</p>
                      <p className="text-slate-500">Vanguard Financial signed $140,000 contract.</p>
                      <span className="text-[10px] text-slate-400">10m ago</span>
                    </div>
                  </div>
                  <div className="p-2 hover:bg-slate-50 rounded-lg flex gap-2">
                    <Clock size={15} className="text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-slate-800">Upcoming Meeting in 30 mins</p>
                      <p className="text-slate-500">CloudScale Contract Review via Google Meet.</p>
                      <span className="text-[10px] text-slate-400">25m ago</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="h-6 w-px bg-slate-200 mx-1" />

          {/* User Profile */}
          <div className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2 p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-semibold flex items-center justify-center text-xs shadow-xs">
                {currentUser?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="hidden lg:flex flex-col text-left">
                <span className="text-xs font-semibold text-slate-800 leading-tight">
                  {currentUser?.full_name || 'Sarah Jenkins'}
                </span>
                <span className="text-[10px] text-slate-400 font-medium leading-tight">
                  {currentUser?.role || 'ADMIN'}
                </span>
              </div>
              <ChevronDown size={13} className="text-slate-400" />
            </button>

            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-xl py-1.5 z-40 text-sm">
                <div className="px-4 py-2 border-b border-slate-100">
                  <p className="font-semibold text-slate-800 text-xs">{currentUser?.full_name}</p>
                  <p className="text-slate-400 text-[11px] truncate">{currentUser?.email}</p>
                  <div className="mt-1.5 inline-block px-1.5 py-0.5 bg-slate-100 text-slate-600 text-[10px] font-medium rounded">
                    {getOrganizationDisplayName(currentUser?.organization_name)}
                  </div>
                </div>

                <Link
                  href="/settings"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 text-slate-700 text-xs"
                >
                  <User size={14} className="text-slate-400" />
                  Organization Settings
                </Link>

                <button
                  onClick={handleLogout}
                  className="w-full text-left flex items-center gap-2 px-4 py-2 hover:bg-red-50 text-red-600 text-xs border-t border-slate-100 mt-1"
                >
                  <LogOut size={14} className="text-red-500" />
                  Log Out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Global Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-start justify-center pt-20 px-4">
          <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            {/* Search Input Bar */}
            <div className="p-4 border-b border-slate-100 flex items-center gap-3">
              <Search size={18} className="text-slate-400" />
              <input
                ref={searchInputRef}
                id="global-search"
                name="global_search"
                type="text"
                autoFocus
                placeholder="Search leads, contacts, deals, accounts, properties..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-slate-800 placeholder-slate-400 text-sm outline-none bg-transparent"
              />
              {isSearching && (
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              )}
              <button
                onClick={() => setShowSearchModal(false)}
                className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
              >
                <X size={16} />
              </button>
            </div>

            {/* Results */}
            <div className="p-4 max-h-96 overflow-y-auto space-y-4">
              {!searchQuery.trim() ? (
                <div className="text-center py-8 text-slate-400 text-xs">
                  Type to search across leads, contacts, deals, accounts, and properties...
                </div>
              ) : Object.keys(searchResults).every((k) => searchResults[k]?.length === 0) ? (
                <div className="text-center py-8 text-slate-500 text-sm">
                  No matching records found for "{searchQuery}".
                </div>
              ) : (
                Object.entries(searchResults).map(([category, items]) => {
                  if (!items || items.length === 0) return null;
                  return (
                    <div key={category}>
                      <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                        {category} ({items.length})
                      </h4>
                      <div className="space-y-1">
                        {items.map((item) => (
                          <Link
                            key={`${item.type}-${item.id}`}
                            href={item.url}
                            onClick={() => setShowSearchModal(false)}
                            className="flex items-center justify-between p-2.5 hover:bg-blue-50/60 rounded-lg group transition-colors"
                          >
                            <div>
                              <div className="text-sm font-medium text-slate-800 group-hover:text-blue-600">
                                {item.title}
                              </div>
                              <div className="text-xs text-slate-400">{item.subtitle}</div>
                            </div>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 group-hover:bg-blue-100 group-hover:text-blue-700 font-medium">
                              {item.type}
                            </span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 text-[11px] text-slate-400 flex items-center justify-between">
              <span>Press <kbd className="px-1 border rounded bg-white font-mono">ESC</kbd> to close</span>
              <span>Multi-Tenant Enterprise Index</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
