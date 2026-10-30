import React from 'react';
import { Phone, Mail, Calendar, FileText, CheckCircle2, RefreshCw, AlertCircle, Clock } from 'lucide-react';
import { Activity } from '@/types/crm';

interface ActivityTimelineProps {
  activities: Activity[];
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400 text-xs bg-slate-50 rounded-xl border border-dashed border-slate-200">
        No recent activities recorded for this timeline.
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'CALL':
        return <Phone size={14} className="text-emerald-600" />;
      case 'EMAIL':
        return <Mail size={14} className="text-blue-600" />;
      case 'MEETING':
        return <Calendar size={14} className="text-purple-600" />;
      case 'NOTE':
        return <FileText size={14} className="text-amber-600" />;
      case 'STATUS_CHANGE':
        return <RefreshCw size={14} className="text-indigo-600" />;
      default:
        return <CheckCircle2 size={14} className="text-slate-500" />;
    }
  };

  const getBadgeBg = (type: string) => {
    switch (type) {
      case 'CALL':
        return 'bg-emerald-50 border-emerald-200';
      case 'EMAIL':
        return 'bg-blue-50 border-blue-200';
      case 'MEETING':
        return 'bg-purple-50 border-purple-200';
      case 'NOTE':
        return 'bg-amber-50 border-amber-200';
      case 'STATUS_CHANGE':
        return 'bg-indigo-50 border-indigo-200';
      default:
        return 'bg-slate-100 border-slate-200';
    }
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {activities.map((act) => (
        <div key={act.id} className="relative group">
          {/* Node Icon */}
          <div className={`absolute -left-6 top-0.5 w-5 h-5 rounded-full border flex items-center justify-center bg-white shadow-xs ${getBadgeBg(act.activity_type)}`}>
            {getIcon(act.activity_type)}
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs hover:border-slate-300 transition-all">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-xs font-semibold text-slate-800">{act.subject}</span>
              <span className="text-[10px] text-slate-400 font-medium">
                {new Date(act.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            {act.description && (
              <p className="text-xs text-slate-600 leading-relaxed mb-2">
                {act.description}
              </p>
            )}

            <div className="flex items-center justify-between text-[10px] text-slate-400">
              <span>Logged by: <strong className="text-slate-600 font-medium">{act.created_by_name || 'System'}</strong></span>
              <span className="uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-500">
                {act.activity_type.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

