'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, Home, GraduationCap, Landmark, Stethoscope,
  ShoppingBag, Cloud, Plus, Calendar, DollarSign, User, CheckCircle
} from 'lucide-react';
import { crmApi } from '@/lib/api';

export default function IndustryDetailPage() {
  const params = useParams();
  const industryId = params?.industry as string;

  const [activeTab, setActiveTab] = useState('main');
  const [data, setData] = useState<any[]>([]);
  const [secondaryData, setSecondaryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const fetchData = async () => {
      try {
        if (industryId === 'real-estate') {
          const [props, visits] = await Promise.all([
            crmApi.getProperties(),
            crmApi.getSiteVisits(),
          ]);
          setData(props);
          setSecondaryData(visits);
        } else if (industryId === 'edtech') {
          const [courses, apps] = await Promise.all([
            crmApi.getCourses(),
            crmApi.getStudentApplications(),
          ]);
          setData(courses);
          setSecondaryData(apps);
        } else if (industryId === 'bfsi') {
          const portfolios = await crmApi.getClientPortfolios();
          setData(portfolios);
        } else if (industryId === 'healthcare') {
          const appts = await crmApi.getHealthcareAppointments();
          setData(appts);
        } else if (industryId === 'ecommerce') {
          const orders = await crmApi.getEcommerceOrders();
          setData(orders);
        } else if (industryId === 'b2b-saas') {
          const [props, subs] = await Promise.all([
            crmApi.getSaaSProposals(),
            crmApi.getSaaSSubscriptions(),
          ]);
          setData(props);
          setSecondaryData(subs);
        }
      } catch (err) {
        console.error('Error fetching industry data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [industryId]);

  const titles: Record<string, { title: string; subtitle: string }> = {
    'real-estate': { title: 'Real Estate & Property Management', subtitle: 'Property units, broker assignments, buyer matching, and on-site visits' },
    'edtech': { title: 'EdTech & Course Admissions', subtitle: 'Curriculum catalog, student applications, counselling cadences, and enrollments' },
    'bfsi': { title: 'BFSI & Wealth Management', subtitle: 'Institutional client asset portfolios, document compliance, and renewals' },
    'healthcare': { title: 'Healthcare & Patient Management', subtitle: 'Clinical consultation schedules, provider rosters, and follow-ups' },
    'ecommerce': { title: 'E-Commerce & D2C Retail', subtitle: 'Order fulfillments, omnichannel support tickets, and abandoned cart events' },
    'b2b-saas': { title: 'B2B SaaS & Subscription Operations', subtitle: 'Annual SaaS contract proposals, recurring revenue, and onboarding milestones' },
  };

  const currentInfo = titles[industryId] || { title: 'Industry Module', subtitle: 'Enterprise vertical operations' };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center gap-3">
          <Link
            href="/industry-modules"
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-500"
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">{currentInfo.title}</h1>
            <p className="text-xs text-slate-500 mt-0.5">{currentInfo.subtitle}</p>
          </div>
        </div>

        <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200 self-start sm:self-auto">
          Connected to PostgreSQL
        </span>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('main')}
          className={`px-3 py-1.5 rounded-lg transition-colors ${
            activeTab === 'main' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          Primary Records ({data.length})
        </button>
        {secondaryData.length > 0 && (
          <button
            onClick={() => setActiveTab('secondary')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'secondary' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-500 hover:bg-slate-100'
            }`}
          >
            Secondary Workflows ({secondaryData.length})
          </button>
        )}
      </div>

      {/* Content Rendering based on Industry */}
      {loading ? (
        <div className="py-24 text-center text-slate-400 text-xs">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading module records...
        </div>
      ) : activeTab === 'main' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {data.map((item, idx) => (
            <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 uppercase">
                    {item.status || item.stage || item.category || 'Active'}
                  </span>
                  {item.price && (
                    <span className="font-bold text-slate-900 text-sm">${item.price?.toLocaleString()}</span>
                  )}
                  {item.fee && (
                    <span className="font-bold text-slate-900 text-sm">${item.fee?.toLocaleString()}</span>
                  )}
                  {item.total_asset_value && (
                    <span className="font-bold text-slate-900 text-sm">${item.total_asset_value?.toLocaleString()}</span>
                  )}
                  {item.order_value && (
                    <span className="font-bold text-slate-900 text-sm">${item.order_value?.toLocaleString()}</span>
                  )}
                  {item.annual_recurring_revenue && (
                    <span className="font-bold text-blue-600 text-sm">${item.annual_recurring_revenue?.toLocaleString()} ARR</span>
                  )}
                </div>

                <h3 className="font-bold text-slate-900 text-sm mb-1">
                  {item.title || item.client_name || item.patient_name || item.order_number || item.prospect_company || item.name}
                </h3>

                <p className="text-xs text-slate-500 mb-3">
                  {item.location || item.applicant_email || item.reason_for_visit || item.shipping_address || item.contact_email || item.department || 'Active tenant entity'}
                </p>

                {item.area_sqft && (
                  <div className="text-xs text-slate-600 space-x-2">
                    <span>{item.bedrooms} Beds</span>
                    <span>&bull;</span>
                    <span>{item.bathrooms} Baths</span>
                    <span>&bull;</span>
                    <span>{item.area_sqft} sq.ft</span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Created: {new Date(item.created_at || Date.now()).toLocaleDateString()}</span>
                <span className="font-semibold text-blue-600">Details &rarr;</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Secondary Tab View */
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs divide-y divide-slate-100">
          {secondaryData.map((item, idx) => (
            <div key={idx} className="p-4 flex items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors">
              <div>
                <h4 className="text-xs font-bold text-slate-900">
                  {item.visitor_name || item.applicant_name || item.company_name || 'Workflow Item'}
                </h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  {item.feedback || item.notes || `MRR: $${item.mrr} &bull; ${item.seats} seats`}
                </p>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                {item.status || item.stage || 'Completed'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

