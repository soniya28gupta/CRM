'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Bot, Send, Sparkles, User, ArrowRight, CornerDownLeft } from 'lucide-react';
import { AIChatMessage } from '@/types/crm';
import { crmApi } from '@/lib/api';

const QUICK_PROMPTS = [
  'Which open deals have the highest value?',
  'How many deals are in negotiation?',
  'Summarize my upcoming meetings',
  'Show overdue tasks and follow-ups',
  'Show top scored leads',
  'Revenue pipeline summary'
];

export const AIChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<AIChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am your AI CRM Assistant with real-time, authorized access to your organization's CRM records. You can ask me natural language queries about your pipeline, leads, meetings, and revenue.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggested_actions: [
        'Which open deals have the highest value?',
        'How many deals are in negotiation?',
        'Summarize upcoming meetings'
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || loading) return;

    const userMsg: AIChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await crmApi.sendAIChat(textToSend);
      const assistantMsg: AIChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggested_actions: res.suggested_actions,
        related_records: res.related_records
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: AIChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: `Error processing query: ${err.message || 'Service unavailable.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[calc(100vh-140px)] max-h-[800px] overflow-hidden">
      {/* Assistant Header */}
      <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-600/20">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              NexusCRM AI Copilot
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                Live Data Connected
              </span>
            </h3>
            <p className="text-[11px] text-slate-500">Secure organization-isolated queries with role-based permission checks</p>
          </div>
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-purple-600 text-white'
              }`}
            >
              {msg.sender === 'user' ? <User size={15} /> : <Bot size={15} />}
            </div>

            <div
              className={`max-w-xl rounded-2xl p-4 text-xs leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-slate-50 text-slate-800 border border-slate-200 rounded-tl-none space-y-2'
              }`}
            >
              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Related Records Cards */}
              {msg.related_records && msg.related_records.length > 0 && (
                <div className="pt-2 border-t border-slate-200/60 space-y-1.5">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Direct CRM Records
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {msg.related_records.map((rec, i) => (
                      <div
                        key={i}
                        className="p-2 bg-white rounded-lg border border-slate-200 flex items-center justify-between text-slate-800 hover:border-blue-400 transition-colors"
                      >
                        <div className="truncate">
                          <span className="font-semibold block truncate">{rec.name}</span>
                          <span className="text-[10px] text-slate-400 uppercase">{rec.type}</span>
                        </div>
                        {rec.value && (
                          <span className="font-bold text-blue-600 text-[11px] shrink-0 ml-2">
                            {rec.value}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Follow-ups */}
              {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                <div className="pt-2 flex flex-wrap gap-1.5">
                  {msg.suggested_actions.map((action, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(action)}
                      className="text-[10px] bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-full px-2.5 py-1 font-medium transition-colors"
                    >
                      {action} &rarr;
                    </button>
                  ))}
                </div>
              )}

              <div
                className={`text-[9px] mt-1 text-right ${
                  msg.sender === 'user' ? 'text-blue-200' : 'text-slate-400'
                }`}
              >
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400 pl-11">
            <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
            <span>AI Copilot is querying authorized records...</span>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompts Bar */}
      <div className="px-6 py-2 bg-slate-50/70 border-t border-slate-100 flex items-center gap-2 overflow-x-auto">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider shrink-0">Quick Queries:</span>
        {QUICK_PROMPTS.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            className="text-[11px] whitespace-nowrap px-2.5 py-1 rounded-full bg-white border border-slate-200 text-slate-600 hover:border-purple-300 hover:text-purple-700 transition-colors shrink-0 shadow-xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-slate-100 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:border-purple-600 focus-within:ring-1 focus-within:ring-purple-600 transition-all"
        >
          <input
            type="text"
            placeholder="Ask anything about deals, leads, meetings, or revenues..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent text-xs text-slate-800 placeholder-slate-400 outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:opacity-40 text-white transition-all shadow-xs"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
};
