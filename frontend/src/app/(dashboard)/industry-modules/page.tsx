'use client';

import React from 'react';
import Link from 'next/link';
import {
  Home, GraduationCap, Landmark, Stethoscope, ShoppingBag,
  Cloud, ArrowRight, CheckCircle2, Sparkles
} from 'lucide-react';

const MODULES = [
  {
    id: 'real-estate',
    name: 'Real Estate & Construction',
    icon: Home,
    color: 'bg-amber-500',
    tag: 'Flagship Vertical',
    description: 'Property inventory, luxury units, buyer leads, site visits, and booking workflows.',
    features: ['Property Listings & Pricing', 'Site Visit Scheduling', 'Booking Transactions', 'Construction Projects'],
    workflow: 'Lead → Property Matching → Site Visit → Negotiation → Booking',
  },
  {
    id: 'edtech',
    name: 'EdTech & Training',
    icon: GraduationCap,
    color: 'bg-blue-500',
    tag: 'Education',
    description: 'Student inquiry management, course enrollments, counsellor assignment, and demo classes.',
    features: ['Course Catalogs', 'Student Applications', 'Demo Class Scheduling', 'Tuition & Enrollments'],
    workflow: 'Inquiry → Counselling → Demo Class → Application → Enrollment',
  },
  {
    id: 'bfsi',
    name: 'BFSI & Finance',
    icon: Landmark,
    color: 'bg-emerald-500',
    tag: 'Wealth & Insurance',
    description: 'Institutional client portfolios, document compliance checklists, and policy renewals.',
    features: ['Client Asset Portfolios', 'Document Compliance', 'Renewal Reminders', 'Risk Profiling'],
    workflow: 'KYC Intake → Risk Profiling → Portfolio Allocation → Annual Renewal',
  },
  {
    id: 'healthcare',
    name: 'Healthcare & Clinics',
    icon: Stethoscope,
    color: 'bg-rose-500',
    tag: 'Clinical Care',
    description: 'Patient consultations, provider schedules, appointment status, and follow-up tracking.',
    features: ['Healthcare Providers', 'Patient Appointments', 'Follow-Up Reminders', 'Clinical History'],
    workflow: 'Patient Inquiry → Provider Matching → Appointment → Follow-up Care',
  },
  {
    id: 'ecommerce',
    name: 'E-Commerce & D2C',
    icon: ShoppingBag,
    color: 'bg-violet-500',
    tag: 'Omnichannel Retail',
    description: 'Order tracking, omnichannel support tickets, cart recovery events, and customer retention.',
    features: ['Customer Order History', 'Support Ticket Management', 'Cart Abandonment Recovery', 'VIP Retention'],
    workflow: 'Abandoned Cart → Recovery Cadence → Order Placement → Support Ticket',
  },
  {
    id: 'b2b-saas',
    name: 'B2B SaaS & Cloud',
    icon: Cloud,
    color: 'bg-cyan-500',
    tag: 'Software Sales',
    description: 'SaaS proposals, ARR contracts, active subscriptions, seat management, and onboarding tasks.',
    features: ['Annual Proposals & Contracts', 'MRR / ARR Subscriptions', 'Customer Onboarding Tasks', 'Seat License Tracking'],
    workflow: 'Prospect → Technical Demo → Commercial Proposal → Subscription Renewal',
  },
];

export default function IndustryModulesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Enterprise Industry Modules</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Domain-specific CRM entities and workflows layered on top of the unified multi-tenant core
        </p>
      </div>

      {/* Grid of 6 modules */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {MODULES.map((mod) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-xs hover:border-blue-400 hover:shadow-md transition-all flex flex-col justify-between overflow-hidden group"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-11 h-11 rounded-xl ${mod.color} text-white flex items-center justify-center shadow-md`}>
                    <Icon size={22} />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 uppercase tracking-wider">
                    {mod.tag}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors mb-1.5">
                  {mod.name}
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed mb-4">
                  {mod.description}
                </p>

                {/* Key Features */}
                <div className="space-y-1.5 mb-4">
                  {mod.features.map((feat, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-700">
                      <CheckCircle2 size={13} className="text-emerald-500 shrink-0" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>

                {/* Workflow Badge */}
                <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-100 text-[10px] text-slate-500">
                  <strong className="text-slate-700 block font-semibold mb-0.5">Core Workflow:</strong>
                  {mod.workflow}
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-semibold text-emerald-600 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Active & Configured
                </span>

                <Link
                  href={`/industry-modules/${mod.id}`}
                  className="flex items-center gap-1.5 text-xs font-bold text-blue-600 group-hover:text-blue-700 group-hover:translate-x-0.5 transition-all"
                >
                  <span>Open Module</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

