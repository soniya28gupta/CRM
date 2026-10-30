export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  role: 'ADMIN' | 'SALES_REP' | 'VIEWER';
  organization_id: number;
  organization_name: string;
}

export interface MetricCardData {
  title: string;
  value: string | number;
  change_percentage?: number | null;
  period: string;
  trend: 'up' | 'down' | 'neutral';
}

export interface DashboardMetrics {
  total_leads: number;
  total_contacts: number;
  conversion_rate: number;
  active_deals: number;
  open_pipeline_value: number;
  weighted_pipeline_value: number;
  closed_won_revenue: number;
  tasks_due_today: number;
  cards: MetricCardData[];
}

export interface ChartDataPoint {
  label: string;
  value: number;
  secondary_value?: number;
}

export interface SalesPerformanceCharts {
  monthly_trend: ChartDataPoint[];
  leads_by_source: ChartDataPoint[];
  leads_by_status: ChartDataPoint[];
  deals_by_stage: ChartDataPoint[];
}

export interface Lead {
  id: number;
  org_id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  lead_source: string;
  industry: string;
  status: 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'UNQUALIFIED' | 'CONVERTED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  estimated_value: number;
  tags?: string;
  notes?: string;
  lead_score: number;
  score_explanation: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  converted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Contact {
  id: number;
  org_id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  account_id?: number;
  account_name?: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  tags?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Account {
  id: number;
  org_id: number;
  name: string;
  industry: string;
  website?: string;
  email?: string;
  phone?: string;
  address?: string;
  company_size?: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  description?: string;
  tags?: string;
  contacts_count: number;
  deals_count: number;
  total_deal_value: number;
  created_at: string;
  updated_at: string;
}

export interface PipelineStage {
  id: number;
  pipeline_id: number;
  name: string;
  stage_order: number;
  probability: number;
  color: string;
}

export interface Deal {
  id: number;
  org_id: number;
  name: string;
  account_id?: number;
  account_name?: string;
  contact_id?: number;
  contact_name?: string;
  pipeline_id: number;
  stage_id: number;
  stage_name?: string;
  value: number;
  currency: string;
  probability: number;
  expected_close_date?: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  source: string;
  description?: string;
  status: 'OPEN' | 'WON' | 'LOST';
  created_at: string;
  updated_at: string;
}

export interface KanbanColumn {
  stage: PipelineStage;
  deals: Deal[];
  total_value: number;
  deal_count: number;
}

export interface KanbanBoardData {
  columns: KanbanColumn[];
  total_pipeline_value: number;
  weighted_pipeline_value: number;
}

export interface Activity {
  id: number;
  org_id: number;
  activity_type: 'CALL' | 'EMAIL' | 'MEETING' | 'NOTE' | 'TASK' | 'STATUS_CHANGE' | 'ASSIGNMENT' | 'SYSTEM';
  subject: string;
  description: string;
  entity_type: string;
  entity_id: number;
  created_by_id?: number;
  created_by_name?: string;
  due_date?: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskItem {
  id: number;
  org_id: number;
  title: string;
  description: string;
  due_date?: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  is_completed: boolean;
  assigned_to_id?: number;
  assigned_to_name?: string;
  entity_type: string;
  entity_id: number;
  created_at: string;
  updated_at: string;
}

export interface MeetingItem {
  id: number;
  org_id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
  attendees: string;
  entity_type: string;
  entity_id: number;
  status: 'SCHEDULED' | 'COMPLETED' | 'CANCELLED';
  created_by_name?: string;
  created_at: string;
}

export interface LeadScoringFactor {
  factor: string;
  score_impact: number;
  reason: string;
}

export interface LeadScoringDetail {
  lead_id: number;
  lead_name: string;
  total_score: number;
  category: 'Hot' | 'Warm' | 'Cold';
  factors: LeadScoringFactor[];
  recommendation: string;
}

export interface AIChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  suggested_actions?: string[];
  related_records?: Array<{
    type: string;
    id: number;
    name: string;
    value?: string;
  }>;
}

export interface GlobalSearchResult {
  id: number;
  title: string;
  subtitle: string;
  url: string;
  type: string;
}
