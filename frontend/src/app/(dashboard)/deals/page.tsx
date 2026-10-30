'use client';

import React, { useState, useEffect } from 'react';
import { Kanban, Plus, RefreshCw, Layers } from 'lucide-react';
import { crmApi } from '@/lib/api';
import { KanbanBoardData } from '@/types/crm';
import { KanbanBoard } from '@/components/deals/KanbanBoard';

export default function DealsPage() {
  const [boardData, setBoardData] = useState<KanbanBoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Deal Form
  const [newDeal, setNewDeal] = useState({
    name: '',
    value: 20000,
    pipeline_id: 1,
    stage_id: 1,
    source: 'Direct Sales',
    description: '',
  });

  const loadBoard = async () => {
    try {
      setLoading(true);
      const data = await crmApi.getKanbanBoard();
      setBoardData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBoard();
  }, []);

  const handleCreateDeal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await crmApi.createDeal(newDeal);
      setNewDeal({ name: '', value: 20000, pipeline_id: 1, stage_id: 1, source: 'Direct Sales', description: '' });
      setShowCreateModal(false);
      loadBoard();
    } catch (err: any) {
      alert(`Error creating deal: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Deals & Sales Pipeline</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-bold border border-blue-200">
              Active Pipeline
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Stage progression, deal values, and win probability tracking
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadBoard}
            className="p-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-semibold"
            title="Refresh Kanban"
          >
            <RefreshCw size={14} />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <Plus size={14} />
            Create Deal
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      {loading || !boardData ? (
        <div className="py-24 text-center text-slate-400 text-xs">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading sales pipeline Kanban board...
        </div>
      ) : (
        <KanbanBoard boardData={boardData} onRefresh={loadBoard} />
      )}

      {/* Create Deal Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-slate-200 shadow-2xl p-6">
            <h3 className="font-bold text-slate-900 text-sm mb-4">Create Commercial Deal</h3>
            <form onSubmit={handleCreateDeal} className="space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Deal Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Corp Enterprise Expansion"
                  value={newDeal.name}
                  onChange={(e) => setNewDeal({ ...newDeal, name: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">Deal Value ($) *</label>
                  <input
                    type="number"
                    required
                    value={newDeal.value}
                    onChange={(e) => setNewDeal({ ...newDeal, value: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">Pipeline Stage</label>
                  <select
                    value={newDeal.stage_id}
                    onChange={(e) => setNewDeal({ ...newDeal, stage_id: Number(e.target.value) })}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  >
                    {boardData?.columns.map((c) => (
                      <option key={c.stage.id} value={c.stage.id}>
                        {c.stage.name} ({c.stage.probability}%)
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Deal Description</label>
                <textarea
                  rows={3}
                  value={newDeal.description}
                  onChange={(e) => setNewDeal({ ...newDeal, description: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                />
              </div>

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
                  Create Opportunity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

