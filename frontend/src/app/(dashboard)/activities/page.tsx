'use client';

import React, { useState, useEffect } from 'react';
import { Clock, Plus, Filter } from 'lucide-react';
import { crmApi } from '@/lib/api';
import { Activity } from '@/types/crm';
import { ActivityTimeline } from '@/components/common/ActivityTimeline';

export default function ActivitiesPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [activityTypeFilter, setActivityTypeFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const loadActivities = async () => {
    try {
      setLoading(true);
      const data = await crmApi.getActivities();
      if (activityTypeFilter !== 'ALL') {
        setActivities(data.filter((a) => a.activity_type === activityTypeFilter));
      } else {
        setActivities(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActivities();
  }, [activityTypeFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Unified Activities Timeline</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold border border-blue-200">
              {activities.length} Recorded Events
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit-grade chronological log of customer calls, emails, status changes, and meeting outcomes
          </p>
        </div>

        {/* Filter */}
        <select
          value={activityTypeFilter}
          onChange={(e) => setActivityTypeFilter(e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-slate-700 outline-none"
        >
          <option value="ALL">All Activity Types</option>
          <option value="CALL">Calls</option>
          <option value="EMAIL">Emails</option>
          <option value="MEETING">Meetings</option>
          <option value="NOTE">Notes</option>
          <option value="STATUS_CHANGE">Status Changes</option>
          <option value="SYSTEM">System Events</option>
        </select>
      </div>

      {/* Timeline Container */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs max-w-3xl">
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading organization timeline...
          </div>
        ) : (
          <ActivityTimeline activities={activities} />
        )}
      </div>
    </div>
  );
}

