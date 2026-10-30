'use client';

import React, { useState } from 'react';
import { KanbanBoardData, Deal } from '@/types/crm';
import { crmApi } from '@/lib/api';
import { MoreHorizontal, DollarSign, Calendar, User, MoveRight, CheckCircle2 } from 'lucide-react';

interface KanbanBoardProps {
  boardData: KanbanBoardData;
  onRefresh: () => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ boardData, onRefresh }) => {
  const [movingDealId, setMovingDealId] = useState<number | null>(null);

  const handleMoveStage = async (dealId: number, targetStageId: number) => {
    try {
      setMovingDealId(dealId);
      await crmApi.updateDealStage(dealId, targetStageId);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to update stage: ${err.message || 'Unknown error'}`);
    } finally {
      setMovingDealId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Board Summary Header */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-6">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Open Pipeline Value</span>
            <span className="text-xl font-bold text-slate-900">${boardData.total_pipeline_value?.toLocaleString()}</span>
          </div>
          <div className="h-8 w-px bg-slate-200" />
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Weighted Pipeline</span>
            <span className="text-xl font-bold text-blue-600">${boardData.weighted_pipeline_value?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
          </div>
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Drag cards or use stage selectors to progress commercial deals.
        </div>
      </div>

      {/* Kanban Columns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 overflow-x-auto pb-4">
        {boardData.columns.map((col) => (
          <div
            key={col.stage.id}
            className="bg-slate-50/80 rounded-xl border border-slate-200 flex flex-col min-w-[260px] max-w-xs shadow-xs"
          >
            {/* Column Header */}
            <div className="p-3 border-b border-slate-200 bg-white rounded-t-xl">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: col.stage.color }}
                  />
                  <span className="font-bold text-slate-800 text-sm">{col.stage.name}</span>
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 font-semibold text-slate-600">
                  {col.deal_count}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
                <span>{col.stage.probability}% Win Prob</span>
                <span className="font-semibold text-slate-700">${col.total_value?.toLocaleString()}</span>
              </div>
            </div>

            {/* Column Cards */}
            <div className="p-2 space-y-2.5 flex-1 overflow-y-auto max-h-[calc(100vh-280px)]">
              {col.deals.length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs border border-dashed border-slate-200 rounded-lg">
                  No deals in this stage
                </div>
              ) : (
                col.deals.map((deal) => (
                  <div
                    key={deal.id}
                    className={`bg-white p-3 rounded-lg border border-slate-200 shadow-xs hover:shadow-sm hover:border-blue-300 transition-all group ${
                      movingDealId === deal.id ? 'opacity-50 pointer-events-none' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-1 mb-1">
                      <h4 className="font-semibold text-slate-800 text-xs leading-snug group-hover:text-blue-600 transition-colors">
                        {deal.name}
                      </h4>
                    </div>

                    <div className="text-[11px] text-slate-500 mb-2 font-medium">
                      {deal.account_name || 'Independent Account'}
                    </div>

                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-100">
                      <span className="text-xs font-bold text-slate-900">
                        ${deal.value?.toLocaleString()}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {deal.expected_close_date
                          ? new Date(deal.expected_close_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                          : 'Q4 Target'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <div className="flex items-center gap-1">
                        <User size={12} className="text-slate-400" />
                        <span className="truncate max-w-[90px]">{deal.assigned_to_name || 'Unassigned'}</span>
                      </div>

                      {/* Quick Move Stage Selector */}
                      <select
                        value={deal.stage_id}
                        onChange={(e) => handleMoveStage(deal.id, Number(e.target.value))}
                        className="text-[10px] bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-slate-600 outline-none cursor-pointer hover:border-slate-300"
                      >
                        {boardData.columns.map((c) => (
                          <option key={c.stage.id} value={c.stage.id}>
                            Move: {c.stage.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

