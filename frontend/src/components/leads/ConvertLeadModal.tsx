'use client';

import React, { useState } from 'react';
import { X, CheckCircle2, Building2, User, DollarSign } from 'lucide-react';
import { Lead } from '@/types/crm';
import { crmApi } from '@/lib/api';

interface ConvertLeadModalProps {
  lead: Lead;
  isOpen: boolean;
  onClose: () => void;
  onConverted: () => void;
}

export const ConvertLeadModal: React.FC<ConvertLeadModalProps> = ({ lead, isOpen, onClose, onConverted }) => {
  const [createAccount, setCreateAccount] = useState(true);
  const [accountName, setAccountName] = useState(lead.company || `${lead.last_name} Enterprises`);
  const [createDeal, setCreateDeal] = useState(true);
  const [dealName, setDealName] = useState(`${lead.company || lead.last_name} - Enterprise Contract`);
  const [dealValue, setDealValue] = useState(lead.estimated_value || 25000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await crmApi.convertLead(lead.id, {
        create_account: createAccount,
        account_name: accountName,
        create_deal: createDeal,
        deal_name: dealName,
        deal_value: dealValue,
      });
      onConverted();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to convert lead.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Convert Lead to Commercial Account</h3>
            <p className="text-xs text-slate-500">{lead.first_name} {lead.last_name} ({lead.company || 'No Company'})</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-200 text-slate-400">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleConvert} className="p-6 space-y-4">
          {error && (
            <div className="p-3 text-xs bg-red-50 text-red-700 border border-red-200 rounded-lg">
              {error}
            </div>
          )}

          {/* Contact Summary */}
          <div className="p-3.5 bg-blue-50/60 rounded-xl border border-blue-100 flex items-start gap-3">
            <User size={18} className="text-blue-600 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-800 text-xs block">Contact Created Automatically</span>
              <span className="text-[11px] text-slate-600">
                {lead.first_name} {lead.last_name} &bull; {lead.email} &bull; {lead.job_title || 'Lead'}
              </span>
            </div>
          </div>

          {/* Account Option */}
          <div className="p-4 border border-slate-200 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs font-bold text-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={createAccount}
                  onChange={(e) => setCreateAccount(e.target.checked)}
                  className="rounded text-blue-600"
                />
                Create Organization Account
              </label>
              <Building2 size={16} className="text-slate-400" />
            </div>

            {createAccount && (
              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Account / Company Name</label>
                <input
                  type="text"
                  required={createAccount}
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                />
              </div>
            )}
          </div>

          {/* Deal Option */}
          <div className="p-4 border border-slate-200 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs font-bold text-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={createDeal}
                  onChange={(e) => setCreateDeal(e.target.checked)}
                  className="rounded text-blue-600"
                />
                Create Pipeline Deal Opportunity
              </label>
              <DollarSign size={16} className="text-slate-400" />
            </div>

            {createDeal && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Deal Name</label>
                  <input
                    type="text"
                    required={createDeal}
                    value={dealName}
                    onChange={(e) => setDealName(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Deal Value ($)</label>
                  <input
                    type="number"
                    required={createDeal}
                    value={dealValue}
                    onChange={(e) => setDealValue(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-blue-600"
                  />
                </div>
              </div>
            )}
          </div>

          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-sm"
            >
              {loading ? 'Converting...' : 'Complete Conversion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

