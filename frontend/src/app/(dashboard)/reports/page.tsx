'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, Users, Award, Download } from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  LineChart, Line, CartesianGrid
} from 'recharts';
import { crmApi } from '@/lib/api';
import { DashboardMetrics, SalesPerformanceCharts } from '@/types/crm';

export default function ReportsPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [charts, setCharts] = useState<SalesPerformanceCharts | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([crmApi.getDashboardMetrics(), crmApi.getDashboardCharts()])
      .then(([m, c]) => {
        setMetrics(m);
        setCharts(c);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">CRM Analytics & Reports</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Transparent conversion formulas, weighted pipeline forecasting, and sales quota pacing
          </p>
        </div>

        <button
          onClick={() => alert('Exporting full analytics PDF / CSV report...')}
          className="flex items-center gap-1.5 px-3.5 py-1.5 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
        >
          <Download size={14} />
          Export Executive Report
        </button>
      </div>

      {/* Formula KPI Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Conversion Rate Formula
            </span>
            <div className="text-2xl font-black text-slate-900">{metrics.conversion_rate}%</div>
            <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono">
              (Converted Leads / Total Leads) &times; 100
            </p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Open Commercial Pipeline
            </span>
            <div className="text-2xl font-black text-blue-600">
              ${metrics.open_pipeline_value?.toLocaleString()}
            </div>
            <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono">
              Sum(Deal Values where Status == OPEN)
            </p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Probability-Weighted Pipeline
            </span>
            <div className="text-2xl font-black text-purple-600">
              ${metrics.weighted_pipeline_value?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </div>
            <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono">
              Sum(Deal Value &times; Win Probability %)
            </p>
          </div>
        </div>
      )}

      {/* Chart Section */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <h3 className="font-bold text-slate-800 text-sm mb-4">Pipeline Value Distribution Across Stages</h3>
        <div className="h-72">
          {charts?.deals_by_stage ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.deals_by_stage}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(val) => `$${val / 1000}k`} />
                <Tooltip
                  formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Stage Total']}
                  contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '11px' }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs">Loading reports...</div>
          )}
        </div>
      </div>
    </div>
  );
}

