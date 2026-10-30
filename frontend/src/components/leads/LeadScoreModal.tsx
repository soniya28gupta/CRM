'use client';

import React, { useState, useEffect } from 'react';
import { X, Sparkles, TrendingUp, CheckCircle, Info } from 'lucide-react';
import { LeadScoringDetail } from '@/types/crm';
import { crmApi } from '@/lib/api';

interface LeadScoreModalProps {
  leadId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export const LeadScoreModal: React.FC<LeadScoreModalProps> = ({ leadId, isOpen, onClose }) => {
  const [scoreData, setScoreData] = useState<LeadScoringDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && leadId) {
      setLoading(true);
      crmApi.getLeadScoreBreakdown(leadId)
        .then((data) => setScoreData(data))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, leadId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-purple-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center text-white">
              <Sparkles size={16} />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">AI Lead Scoring Intelligence</h3>
              <p className="text-[11px] text-slate-500">Transparent factor attribution & conversion forecast</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-200 text-slate-400">
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Computing predictive lead score...
          </div>
        ) : scoreData ? (
          <div className="p-6 space-y-5">
            {/* Score Ring / Bar */}
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
              <div>
                <span className="text-xs text-slate-500 font-medium block">Prospect Name</span>
                <span className="font-bold text-slate-900 text-base">{scoreData.lead_name}</span>
                <span
                  className={`inline-block mt-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    scoreData.category === 'Hot'
                      ? 'bg-rose-100 text-rose-700'
                      : scoreData.category === 'Warm'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {scoreData.category} Lead Priority
                </span>
              </div>

              <div className="text-center">
                <div className="text-3xl font-black text-purple-700">
                  {scoreData.total_score}
                  <span className="text-xs font-semibold text-slate-400">/100</span>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Confidence: 94%</span>
              </div>
            </div>

            {/* Contributing Factors */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <TrendingUp size={14} className="text-purple-600" />
                Contributing Factors
              </h4>
              <div className="space-y-2 max-h-56 overflow-y-auto">
                {scoreData.factors.map((f, i) => (
                  <div key={i} className="p-2.5 rounded-lg border border-slate-100 bg-white hover:border-slate-200 flex items-start justify-between gap-3 text-xs">
                    <div>
                      <div className="font-semibold text-slate-800">{f.factor}</div>
                      <div className="text-[11px] text-slate-500">{f.reason}</div>
                    </div>
                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded shrink-0">
                      +{f.score_impact} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendation */}
            <div className="p-3.5 bg-purple-50 rounded-xl border border-purple-100 flex items-start gap-2.5">
              <Info size={16} className="text-purple-600 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold text-purple-900 block">AI Recommended Next Action</span>
                <p className="text-xs text-purple-800 leading-relaxed mt-0.5">
                  {scoreData.recommendation}
                </p>
              </div>
            </div>
          </div>
        ) : null}

        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold rounded-lg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

