'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Building2, Plus, Search, Globe, Phone, DollarSign, Users, Briefcase } from 'lucide-react';
import { crmApi } from '@/lib/api';
import { Account } from '@/types/crm';

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [industryFilter, setIndustryFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    industry: 'Technology',
    website: '',
    email: '',
    phone: '',
    company_size: '50-200',
    description: '',
  });

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const res = await crmApi.getAccounts({
        search: search.trim() || undefined,
        industry: industryFilter !== 'ALL' ? industryFilter : undefined,
      });
      setAccounts(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, [industryFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await crmApi.createAccount(formData);
      setFormData({ name: '', industry: 'Technology', website: '', email: '', phone: '', company_size: '50-200', description: '' });
      setShowCreateModal(false);
      loadAccounts();
    } catch (err: any) {
      alert(`Error creating account: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Accounts & Institutions</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 font-bold border border-purple-200">
              {total} Organizations
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Enterprise customer entities, parent corporations, and commercial account portfolios
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
        >
          <Plus size={14} />
          Add Account
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            loadAccounts();
          }}
          className="flex items-center gap-2 max-w-md flex-1"
        >
          <div className="relative w-full">
            <Search size={15} className="absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by company name, domain, email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs outline-none focus:border-blue-600 focus:bg-white"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
          >
            Search
          </button>
        </form>

        <select
          value={industryFilter}
          onChange={(e) => setIndustryFilter(e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 outline-none"
        >
          <option value="ALL">All Industries</option>
          <option value="Technology">Technology</option>
          <option value="Healthcare">Healthcare</option>
          <option value="BFSI">BFSI</option>
          <option value="Real Estate">Real Estate</option>
          <option value="Retail & E-commerce">Retail & E-commerce</option>
        </select>
      </div>

      {/* Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 py-16 text-center text-slate-400 text-xs">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading accounts...
          </div>
        ) : accounts.length === 0 ? (
          <div className="col-span-3 py-16 text-center text-slate-400 text-xs">
            No accounts found matching criteria.
          </div>
        ) : (
          accounts.map((acc) => (
            <div
              key={acc.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-slate-300 hover:shadow-sm transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm shrink-0">
                    <Building2 size={18} />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                    {acc.industry}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-sm mb-1">{acc.name}</h3>
                {acc.description && (
                  <p className="text-xs text-slate-500 line-clamp-2 mb-3">{acc.description}</p>
                )}

                <div className="space-y-1.5 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  {acc.website && (
                    <div className="flex items-center gap-2">
                      <Globe size={13} className="text-slate-400" />
                      <a href={acc.website} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline truncate">
                        {acc.website.replace('https://', '')}
                      </a>
                    </div>
                  )}
                  {acc.email && (
                    <div className="flex items-center gap-2 text-slate-500 truncate">
                      <span>Email:</span>
                      <span className="truncate">{acc.email}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Account Metrics Bar */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Total Pipeline</span>
                  <span className="font-bold text-blue-600 text-sm">
                    ${acc.total_deal_value?.toLocaleString()}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Engagements</span>
                  <span className="font-medium text-slate-800">
                    {acc.contacts_count} Contacts &bull; {acc.deals_count} Deals
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-2xl p-6">
            <h3 className="font-bold text-slate-900 text-sm mb-4">Create Organization Account</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                type="text"
                required
                placeholder="Account / Company Name *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <select
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              >
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="BFSI">BFSI</option>
                <option value="Real Estate">Real Estate</option>
                <option value="Retail & E-commerce">Retail & E-commerce</option>
              </select>
              <input
                type="text"
                placeholder="Website (https://...)"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <input
                type="email"
                placeholder="Company Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <textarea
                placeholder="Account Description"
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 text-xs border border-slate-200 rounded-lg text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold shadow-xs"
                >
                  Save Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

