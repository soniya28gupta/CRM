'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, Plus, Video, Clock, Users, MapPin } from 'lucide-react';
import { crmApi } from '@/lib/api';
import { MeetingItem } from '@/types/crm';

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [newMeeting, setNewMeeting] = useState({
    title: '',
    description: '',
    start_time: new Date(Date.now() + 86400000).toISOString().slice(0, 16),
    end_time: new Date(Date.now() + 90000000).toISOString().slice(0, 16),
    location: 'Google Meet',
    attendees: '',
  });

  const loadMeetings = async () => {
    try {
      setLoading(true);
      const data = await crmApi.getMeetings();
      setMeetings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMeetings();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await crmApi.createMeeting(newMeeting);
      setShowCreateModal(false);
      loadMeetings();
    } catch (err: any) {
      alert(`Error creating meeting: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Meeting Schedule</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 font-bold border border-purple-200">
              {meetings.length} Scheduled
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Prospect product demonstrations, client architecture reviews, and follow-up syncs
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
        >
          <Plus size={14} />
          Schedule Meeting
        </button>
      </div>

      {/* Meeting Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-3 py-16 text-center text-slate-400 text-xs">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading scheduled meetings...
          </div>
        ) : meetings.length === 0 ? (
          <div className="col-span-3 py-16 text-center text-slate-400 text-xs">
            No upcoming meetings in calendar.
          </div>
        ) : (
          meetings.map((m) => (
            <div
              key={m.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                    {m.status}
                  </span>
                  <div className="flex items-center gap-1 text-[11px] text-blue-600 font-medium">
                    <Video size={13} />
                    <span>{m.location}</span>
                  </div>
                </div>

                <h3 className="font-bold text-slate-900 text-sm mb-1">{m.title}</h3>
                {m.description && (
                  <p className="text-xs text-slate-500 mb-3">{m.description}</p>
                )}

                <div className="space-y-1.5 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  <div className="flex items-center gap-2">
                    <Clock size={13} className="text-slate-400" />
                    <span>{new Date(m.start_time).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}</span>
                  </div>
                  {m.attendees && (
                    <div className="flex items-center gap-2 text-slate-500 truncate">
                      <Users size={13} className="text-slate-400" />
                      <span className="truncate">{m.attendees}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Host: {m.created_by_name || 'Sarah Jenkins'}</span>
                <span className="font-medium text-blue-600 hover:underline cursor-pointer">
                  Join Meeting &rarr;
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Schedule Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-2xl p-6">
            <h3 className="font-bold text-slate-900 text-sm mb-4">Schedule Client Meeting</h3>
            <form onSubmit={handleCreate} className="space-y-3">
              <input
                type="text"
                required
                placeholder="Meeting Title *"
                value={newMeeting.title}
                onChange={(e) => setNewMeeting({ ...newMeeting, title: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <textarea
                placeholder="Agenda and notes"
                rows={2}
                value={newMeeting.description}
                onChange={(e) => setNewMeeting({ ...newMeeting, description: e.target.value })}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
              />
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Start Time</label>
                  <input
                    type="datetime-local"
                    value={newMeeting.start_time}
                    onChange={(e) => setNewMeeting({ ...newMeeting, start_time: e.target.value })}
                    className="w-full px-2 py-1 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">End Time</label>
                  <input
                    type="datetime-local"
                    value={newMeeting.end_time}
                    onChange={(e) => setNewMeeting({ ...newMeeting, end_time: e.target.value })}
                    className="w-full px-2 py-1 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  />
                </div>
              </div>
              <input
                type="text"
                placeholder="Attendees (comma separated emails)"
                value={newMeeting.attendees}
                onChange={(e) => setNewMeeting({ ...newMeeting, attendees: e.target.value })}
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
                  Confirm Meeting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

