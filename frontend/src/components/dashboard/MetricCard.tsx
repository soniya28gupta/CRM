import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MetricCardData } from '@/types/crm';

interface MetricCardProps {
  card: MetricCardData;
}

export const MetricCard: React.FC<MetricCardProps> = ({ card }) => {
  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-slate-300 hover:shadow-sm transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{card.title}</span>
        {card.change_percentage !== undefined && card.change_percentage !== null && (
          <div
            className={`flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
              card.trend === 'up'
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : card.trend === 'down'
                ? 'bg-rose-50 text-rose-700 border border-rose-200'
                : 'bg-slate-100 text-slate-600'
            }`}
          >
            {card.trend === 'up' && <TrendingUp size={12} />}
            {card.trend === 'down' && <TrendingDown size={12} />}
            {card.trend === 'neutral' && <Minus size={12} />}
            <span>{card.change_percentage > 0 ? `+${card.change_percentage}%` : `${card.change_percentage}%`}</span>
          </div>
        )}
      </div>

      <div className="text-2xl font-bold text-slate-900 tracking-tight mb-1">
        {card.value}
      </div>

      <div className="text-[11px] text-slate-400 font-medium">
        {card.period}
      </div>
    </div>
  );
};
