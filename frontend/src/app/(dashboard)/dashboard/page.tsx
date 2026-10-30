'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Users, UserCheck, Kanban, DollarSign, Calendar, CheckSquare,
  Sparkles, ArrowUpRight, Plus, RefreshCw, Clock, Building2
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from 'recharts';
import { crmApi } from '@/lib/api';
import { DashboardMetrics, SalesPerformanceCharts, Lead } from '@/types/crm';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { LeadModal } from '@/components/leads/LeadModal';

const COLORS = ['#2563eb', '#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [charts, setCharts] = useState<SalesPerformanceCharts | null>(null);
  const [recentLeads, setRecentLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLeadModal, setShowLeadModal] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [m, c, l] = await Promise.all([
        crmApi.getDashboardMetrics(),
        crmApi.getDashboardCharts(),
        crmApi.getLeads({ pageSize: 5 }),
      ]);
      setMetrics(m);
      setCharts(c);
      setRecentLeads(l.items);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Executive CRM Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time pipeline performance, AI scoring indicators, and organization metrics
          </p>
        </div>

        {/* Quick Actions Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setShowLeadModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <Plus size={14} />
            Add Lead
          </button>
          <Link
            href="/deals"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
          >
            <Kanban size={14} />
            View Pipeline
          </Link>
          <Link
            href="/ai-assistant"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-lg text-xs font-semibold transition-colors"
          >
            <Sparkles size={14} className="text-purple-600" />
            AI Query
          </Link>
          <button
            onClick={loadData}
            title="Refresh metrics"
            className="p-1.5 rounded-lg border border-slate-200 text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* 6 Metric Cards */}
      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {metrics.cards.map((c, i) => (
            <MetricCard key={i} card={c} />
          ))}
        </div>
      )}

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales Performance Trend */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Monthly Lead & Conversion Trend</h3>
              <p className="text-xs text-slate-400">Leads created and converted in each of the last six months</p>
            </div>
          </div>

          <div className="h-64">
            {charts?.monthly_trend ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts.monthly_trend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    formatter={(value: any, name: string) => [
                      Number(value).toLocaleString(),
                      name === 'secondary_value' ? 'Converted leads' : 'New leads'
                    ]}
                    contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '11px' }}
                  />
                  <Bar dataKey="value" name="New leads" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="secondary_value" name="Converted leads" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">Loading chart data...</div>
            )}
          </div>
        </div>

        {/* Leads by Source Donut */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="mb-4">
            <h3 className="font-bold text-slate-800 text-sm">Leads by Acquisition Source</h3>
            <p className="text-xs text-slate-400">Distribution across marketing channels</p>
          </div>

          <div className="h-64 flex items-center justify-center">
            {charts?.leads_by_source ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts.leads_by_source}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {charts.leads_by_source.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: any, name: any, item: any) => [value, item.payload.label]}
                    contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '11px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-xs">Loading source breakdown...</div>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2 text-[10px] text-slate-500">
            {charts?.leads_by_source?.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                <span>{item.label} ({item.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Leads & Pipeline Stages Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent High-Priority Leads */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Recently Created Leads & AI Score</h3>
              <p className="text-xs text-slate-400">Automated B2B lead qualification rankings</p>
            </div>
            <Link href="/leads" className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
              View all leads &rarr;
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="pb-2">Lead Name</th>
                  <th className="pb-2">Company</th>
                  <th className="pb-2">Source</th>
                  <th className="pb-2">Est. Value</th>
                  <th className="pb-2">AI Score</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentLeads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-2.5 font-medium text-slate-900">
                      <Link href={`/leads/${lead.id}`} className="hover:text-blue-600">
                        {lead.first_name} {lead.last_name}
                      </Link>
                    </td>
                    <td className="py-2.5 text-slate-600">{lead.company || '—'}</td>
                    <td className="py-2.5 text-slate-500">{lead.lead_source}</td>
                    <td className="py-2.5 font-semibold text-slate-800">${lead.estimated_value?.toLocaleString()}</td>
                    <td className="py-2.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold ${
                          lead.lead_score >= 80
                            ? 'bg-rose-50 text-rose-700 border border-rose-200'
                            : lead.lead_score >= 50
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        <Sparkles size={11} />
                        {lead.lead_score}/100
                      </span>
                    </td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-medium">
                        {lead.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pipeline Value By Stage */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Pipeline Stages Value</h3>
              <p className="text-xs text-slate-400">Total active commercial deal volume</p>
            </div>
            <Link href="/deals" className="text-xs font-semibold text-blue-600 hover:text-blue-700">
              Kanban
            </Link>
          </div>

          <div className="space-y-3">
            {charts?.deals_by_stage?.map((stg, i) => (
              <div key={i} className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/50 flex items-center justify-between text-xs">
                <div>
                  <div className="font-semibold text-slate-800">{stg.label}</div>
                  <div className="text-[10px] text-slate-400">{stg.secondary_value || 0} deal(s) active</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">${stg.value?.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Lead Create Modal */}
      <LeadModal
        isOpen={showLeadModal}
        onClose={() => setShowLeadModal(false)}
        onSuccess={() => {
          loadData();
          setShowLeadModal(false);
        }}
      />
    </div>
  );
}
