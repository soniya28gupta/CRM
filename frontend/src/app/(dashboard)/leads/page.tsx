'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Users, Plus, Search, Filter, Download, Sparkles,
  ArrowRight, Phone, Mail, Building2, MoreHorizontal, CheckCircle2
} from 'lucide-react';
import { crmApi } from '@/lib/api';
import { Lead } from '@/types/crm';
import { LeadModal } from '@/components/leads/LeadModal';
import { ConvertLeadModal } from '@/components/leads/ConvertLeadModal';
import { LeadScoreModal } from '@/components/leads/LeadScoreModal';

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [industryFilter, setIndustryFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLeadForScore, setSelectedLeadForScore] = useState<number | null>(null);
  const [selectedLeadForConvert, setSelectedLeadForConvert] = useState<Lead | null>(null);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const res = await crmApi.getLeads({
        page,
        pageSize: 10,
        search: search.trim() || undefined,
        status: statusFilter,
        priority: priorityFilter,
        industry: industryFilter,
      });
      setLeads(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error fetching leads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [page, statusFilter, priorityFilter, industryFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLeads();
  };

  const handleExportCSV = () => {
    window.open('/api/leads/export/csv', '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Leads Management</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold border border-blue-200">
              {total} Total Leads
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            AI-prioritized qualification pipeline with automated conversion workflows
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold transition-colors"
          >
            <Download size={14} />
            Export CSV
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <Plus size={14} />
            New Lead
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-md">
          <div className="relative w-full">
            <Search size={15} className="absolute left-3 top-2.5 text-slate-400" />
            <input
              id="lead-search"
              name="search"
              type="text"
              placeholder="Search by name, email, company, tags..."
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

        <div className="flex flex-wrap items-center gap-2">
          {/* Status Filter */}
          <select
            id="lead-status-filter"
            name="status_filter"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="CONTACTED">Contacted</option>
            <option value="QUALIFIED">Qualified</option>
            <option value="CONVERTED">Converted</option>
          </select>

          {/* Priority Filter */}
          <select
            id="lead-priority-filter"
            name="priority_filter"
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 outline-none"
          >
            <option value="ALL">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Industry Filter */}
          <select
            id="lead-industry-filter"
            name="industry_filter"
            value={industryFilter}
            onChange={(e) => {
              setIndustryFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 outline-none"
          >
            <option value="ALL">All Industries</option>
            <option value="Technology">Technology</option>
            <option value="Real Estate">Real Estate</option>
            <option value="EdTech">EdTech</option>
            <option value="BFSI">BFSI</option>
            <option value="Healthcare">Healthcare</option>
            <option value="E-Commerce">E-Commerce</option>
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Lead Name & Job</th>
                <th className="py-3 px-4">Contact Info</th>
                <th className="py-3 px-4">Company & Industry</th>
                <th className="py-3 px-4">Est. Value</th>
                <th className="py-3 px-4">AI Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-400">
                    <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    Loading qualified leads...
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-400">
                    No leads match the selected criteria.
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/70 transition-colors group">
                    {/* Name & Title */}
                    <td className="py-3 px-4">
                      <Link href={`/leads/${lead.id}`} className="font-semibold text-slate-900 group-hover:text-blue-600">
                        {lead.first_name} {lead.last_name}
                      </Link>
                      <div className="text-[11px] text-slate-400">{lead.job_title || 'Lead Prospect'}</div>
                    </td>

                    {/* Email & Phone */}
                    <td className="py-3 px-4 space-y-0.5">
                      <div className="flex items-center gap-1.5 text-slate-600">
                        <Mail size={12} className="text-slate-400" />
                        <span>{lead.email}</span>
                      </div>
                      {lead.phone && (
                        <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                          <Phone size={12} />
                          <span>{lead.phone}</span>
                        </div>
                      )}
                    </td>

                    {/* Company */}
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-800">{lead.company || '—'}</div>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium">
                        {lead.industry}
                      </span>
                    </td>

                    {/* Deal Value */}
                    <td className="py-3 px-4 font-bold text-slate-900">
                      ${lead.estimated_value?.toLocaleString()}
                    </td>

                    {/* AI Score Badge */}
                    <td className="py-3 px-4">
                      <button
                        onClick={() => setSelectedLeadForScore(lead.id)}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold transition-transform hover:scale-105 ${
                          lead.lead_score >= 80
                            ? 'bg-rose-50 text-rose-700 border border-rose-200'
                            : lead.lead_score >= 50
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-slate-100 text-slate-600 border border-slate-200'
                        }`}
                        title="Click to view AI factor breakdown"
                      >
                        <Sparkles size={12} />
                        {lead.lead_score}/100
                      </button>
                    </td>

                    {/* Status */}
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          lead.status === 'CONVERTED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : lead.status === 'QUALIFIED'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {lead.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right space-x-1.5">
                      {lead.status !== 'CONVERTED' && (
                        <button
                          onClick={() => setSelectedLeadForConvert(lead)}
                          className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded text-[11px] border border-emerald-200 transition-colors"
                        >
                          Convert
                        </button>
                      )}
                      <Link
                        href={`/leads/${lead.id}`}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded text-[11px] transition-colors"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>Page {page} of {totalPages} ({total} leads)</span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1 bg-white border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-100 text-xs font-semibold"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1 bg-white border border-slate-200 rounded disabled:opacity-40 hover:bg-slate-100 text-xs font-semibold"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      <LeadModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          fetchLeads();
          setShowCreateModal(false);
        }}
      />

      <LeadScoreModal
        leadId={selectedLeadForScore}
        isOpen={selectedLeadForScore !== null}
        onClose={() => setSelectedLeadForScore(null)}
      />

      {selectedLeadForConvert && (
        <ConvertLeadModal
          lead={selectedLeadForConvert}
          isOpen={true}
          onClose={() => setSelectedLeadForConvert(null)}
          onConverted={() => {
            fetchLeads();
            setSelectedLeadForConvert(null);
          }}
        />
      )}
    </div>
  );
}
