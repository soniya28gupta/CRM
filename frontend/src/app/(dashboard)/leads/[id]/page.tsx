'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, Mail, Phone, Building2, Briefcase, Calendar,
  Sparkles, CheckCircle, Plus, Clock, Edit3, Trash2
} from 'lucide-react';
import { crmApi } from '@/lib/api';
import { Lead, Activity } from '@/types/crm';
import { ActivityTimeline } from '@/components/common/ActivityTimeline';
import { ConvertLeadModal } from '@/components/leads/ConvertLeadModal';
import { LeadScoreModal } from '@/components/leads/LeadScoreModal';
import { LeadModal } from '@/components/leads/LeadModal';

export default function LeadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const leadId = Number(params?.id);

  const [lead, setLead] = useState<Lead | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  // Quick activity log state
  const [noteText, setNoteText] = useState('');
  const [logType, setLogType] = useState<'NOTE' | 'CALL' | 'EMAIL'>('NOTE');
  const [submittingAct, setSubmittingAct] = useState(false);

  // Modals
  const [showEditModal, setShowEditModal] = useState(false);
  const [showConvertModal, setShowConvertModal] = useState(false);
  const [showScoreModal, setShowScoreModal] = useState(false);

  const loadLeadData = async () => {
    if (!leadId) return;
    try {
      setLoading(true);
      const [l, acts] = await Promise.all([
        crmApi.getLead(leadId),
        crmApi.getActivities('lead', leadId),
      ]);
      setLead(l);
      setActivities(acts);
    } catch (err) {
      console.error('Error fetching lead detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeadData();
  }, [leadId]);

  const handleAddActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;

    setSubmittingAct(true);
    try {
      await crmApi.createActivity({
        activity_type: logType,
        subject: `${logType} logged for ${lead?.first_name} ${lead?.last_name}`,
        description: noteText,
        entity_type: 'lead',
        entity_id: leadId,
        is_completed: true,
      });
      setNoteText('');
      loadLeadData();
    } catch (err: any) {
      alert(`Error logging activity: ${err.message}`);
    } finally {
      setSubmittingAct(false);
    }
  };

  const handleDeleteLead = async () => {
    if (confirm('Are you sure you want to delete this lead? This action cannot be undone.')) {
      await crmApi.deleteLead(leadId);
      router.push('/leads');
    }
  };

  if (loading || !lead) {
    return (
      <div className="py-24 text-center text-slate-400 text-xs">
        <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        Loading lead details...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-3">
          <Link
            href="/leads"
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500"
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                {lead.first_name} {lead.last_name}
              </h1>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  lead.status === 'CONVERTED'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {lead.status}
              </span>
            </div>
            <p className="text-xs text-slate-500">{lead.job_title || 'Lead Prospect'} at {lead.company || 'Direct Inbound'}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {lead.status !== 'CONVERTED' && (
            <button
              onClick={() => setShowConvertModal(true)}
              className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
            >
              Convert to Deal
            </button>
          )}
          <button
            onClick={() => setShowEditModal(true)}
            className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5"
          >
            <Edit3 size={14} />
            Edit
          </button>
          <button
            onClick={handleDeleteLead}
            className="p-1.5 border border-red-200 hover:bg-red-50 text-red-600 rounded-lg text-xs"
            title="Delete Lead"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Lead Overview & AI Score */}
        <div className="space-y-6">
          {/* AI Score Card */}
          <div className="bg-white p-5 rounded-2xl border border-purple-200 shadow-xs relative overflow-hidden">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-purple-700 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles size={14} />
                AI Qualification Score
              </span>
              <button
                onClick={() => setShowScoreModal(true)}
                className="text-[11px] font-semibold text-purple-600 hover:text-purple-700"
              >
                Explain &rarr;
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-3xl font-black text-purple-700">
                {lead.lead_score}
                <span className="text-xs font-semibold text-slate-400">/100</span>
              </div>
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                  lead.lead_score >= 80 ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                }`}
              >
                {lead.lead_score >= 80 ? 'Hot Lead' : 'Warm Priority'}
              </span>
            </div>

            <p className="text-xs text-slate-600 mt-3 leading-relaxed bg-purple-50/50 p-2.5 rounded-lg border border-purple-100">
              {lead.score_explanation || 'Lead score calculated based on executive authority and inbound source.'}
            </p>
          </div>

          {/* Core Properties Card */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider border-b border-slate-100 pb-2">
              Lead Information
            </h3>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Email</span>
                <span className="font-semibold text-slate-800">{lead.email}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Phone</span>
                <span className="font-semibold text-slate-800">{lead.phone || '—'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Source</span>
                <span className="font-semibold text-slate-800">{lead.lead_source}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Industry</span>
                <span className="font-semibold text-slate-800">{lead.industry}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Priority</span>
                <span className="font-semibold text-slate-800">{lead.priority}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Estimated Value</span>
                <span className="font-bold text-blue-600">${lead.estimated_value?.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Assigned Rep</span>
                <span className="font-semibold text-slate-800">{lead.assigned_to_name || 'Sarah Jenkins'}</span>
              </div>
            </div>

            {lead.notes && (
              <div className="pt-3 border-t border-slate-100">
                <span className="text-[11px] font-semibold text-slate-400 block mb-1">Lead Notes:</span>
                <p className="text-xs text-slate-600 bg-slate-50 p-2 rounded-lg">{lead.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Middle & Right: Quick Logger & Activity Timeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quick Activity Logger */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider mb-3">
              Log Activity / Note
            </h3>

            <div className="flex items-center gap-2 mb-3">
              {(['NOTE', 'CALL', 'EMAIL'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setLogType(type)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    logType === type
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  + Log {type}
                </button>
              ))}
            </div>

            <form onSubmit={handleAddActivity} className="space-y-3">
              <textarea
                rows={3}
                required
                placeholder={`Describe outcome of ${logType.toLowerCase()} with prospect...`}
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={submittingAct || !noteText.trim()}
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-xs font-semibold rounded-lg shadow-xs"
                >
                  {submittingAct ? 'Saving...' : 'Save Activity Entry'}
                </button>
              </div>
            </form>
          </div>

          {/* Activity Timeline */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800 text-sm">Interaction History & Timeline</h3>
              <span className="text-xs text-slate-400">{activities.length} total events</span>
            </div>

            <ActivityTimeline activities={activities} />
          </div>
        </div>
      </div>

      {/* Modals */}
      <LeadModal
        lead={lead}
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSuccess={() => {
          loadLeadData();
          setShowEditModal(false);
        }}
      />

      <LeadScoreModal
        leadId={leadId}
        isOpen={showScoreModal}
        onClose={() => setShowScoreModal(false)}
      />

      <ConvertLeadModal
        lead={lead}
        isOpen={showConvertModal}
        onClose={() => setShowConvertModal(false)}
        onConverted={() => {
          loadLeadData();
          setShowConvertModal(false);
        }}
      />
    </div>
  );
}

