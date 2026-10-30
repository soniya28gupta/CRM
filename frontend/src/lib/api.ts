import {
  User, DashboardMetrics, SalesPerformanceCharts,
  Lead, Contact, Account, Deal, KanbanBoardData,
  Activity, TaskItem, MeetingItem, LeadScoringDetail,
  AIChatMessage, GlobalSearchResult
} from '@/types/crm';

const API_BASE = '/api';

export class ApiRequestError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

// Helper for authorized requests
async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new ApiRequestError(
      errorData.detail || `Request failed with status ${res.status}`,
      res.status
    );
  }

  return res.json();
}

export const crmApi = {
  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const data = await fetchWithAuth('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (typeof window !== 'undefined') localStorage.setItem('crm_user', JSON.stringify(data.user));
    return data;
  },

  async register(email: string, password: string, full_name: string, organization_name: string) {
    const data = await fetchWithAuth('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, organization_name }),
    });
    if (typeof window !== 'undefined') localStorage.setItem('crm_user', JSON.stringify(data.user));
    return data;
  },

  async logout(): Promise<void> {
    try {
      await fetchWithAuth('/auth/logout', { method: 'POST' });
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('crm_token');
        localStorage.removeItem('crm_user');
      }
    }
  },

  async getMe(): Promise<User> {
    return fetchWithAuth('/auth/me');
  },

  async getSessionStatus(): Promise<{ authenticated: boolean }> {
    return fetchWithAuth('/auth/session');
  },

  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return fetchWithAuth('/dashboard/metrics');
  },

  async getDashboardCharts(): Promise<SalesPerformanceCharts> {
    return fetchWithAuth('/dashboard/charts');
  },

  // Leads
  async getLeads(params: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string;
    priority?: string;
    industry?: string;
  } = {}): Promise<{ items: Lead[]; total: number; page: number; total_pages: number }> {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page.toString());
    if (params.pageSize) query.set('page_size', params.pageSize.toString());
    if (params.search) query.set('search', params.search);
    if (params.status && params.status !== 'ALL') query.set('status', params.status);
    if (params.priority && params.priority !== 'ALL') query.set('priority', params.priority);
    if (params.industry && params.industry !== 'ALL') query.set('industry', params.industry);
    return fetchWithAuth(`/leads?${query.toString()}`);
  },

  async getLead(id: number): Promise<Lead> {
    return fetchWithAuth(`/leads/${id}`);
  },

  async createLead(leadData: Partial<Lead>): Promise<Lead> {
    return fetchWithAuth('/leads', {
      method: 'POST',
      body: JSON.stringify(leadData),
    });
  },

  async updateLead(id: number, leadData: Partial<Lead>): Promise<Lead> {
    return fetchWithAuth(`/leads/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(leadData),
    });
  },

  async deleteLead(id: number): Promise<void> {
    return fetchWithAuth(`/leads/${id}`, { method: 'DELETE' });
  },

  async getLeadScoreBreakdown(id: number): Promise<LeadScoringDetail> {
    return fetchWithAuth(`/leads/${id}/score`, { method: 'POST' });
  },

  async convertLead(id: number, payload: {
    create_account?: boolean;
    account_name?: string;
    create_deal?: boolean;
    deal_name?: string;
    deal_value?: number;
  }) {
    return fetchWithAuth(`/leads/${id}/convert`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Contacts
  async getContacts(params: { page?: number; search?: string } = {}): Promise<{ items: Contact[]; total: number }> {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page.toString());
    if (params.search) query.set('search', params.search);
    return fetchWithAuth(`/contacts?${query.toString()}`);
  },

  async createContact(contactData: Partial<Contact>): Promise<Contact> {
    return fetchWithAuth('/contacts', {
      method: 'POST',
      body: JSON.stringify(contactData),
    });
  },

  // Accounts
  async getAccounts(params: { page?: number; search?: string; industry?: string } = {}): Promise<{ items: Account[]; total: number }> {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page.toString());
    if (params.search) query.set('search', params.search);
    if (params.industry) query.set('industry', params.industry);
    return fetchWithAuth(`/accounts?${query.toString()}`);
  },

  async createAccount(accData: Partial<Account>): Promise<Account> {
    return fetchWithAuth('/accounts', {
      method: 'POST',
      body: JSON.stringify(accData),
    });
  },

  // Deals & Kanban
  async getDeals(): Promise<Deal[]> {
    return fetchWithAuth('/deals');
  },

  async getKanbanBoard(): Promise<KanbanBoardData> {
    return fetchWithAuth('/deals/kanban');
  },

  async createDeal(dealData: Partial<Deal>): Promise<Deal> {
    return fetchWithAuth('/deals', {
      method: 'POST',
      body: JSON.stringify(dealData),
    });
  },

  async updateDealStage(dealId: number, stageId: number): Promise<Deal> {
    return fetchWithAuth(`/deals/${dealId}/stage`, {
      method: 'PATCH',
      body: JSON.stringify({ stage_id: stageId }),
    });
  },

  // Activities & Tasks
  async getActivities(entityType?: string, entityId?: number): Promise<Activity[]> {
    const query = new URLSearchParams();
    if (entityType && entityId) {
      query.set('entity_type', entityType);
      query.set('entity_id', entityId.toString());
    }
    return fetchWithAuth(`/activities?${query.toString()}`);
  },

  async createActivity(activityData: Partial<Activity>): Promise<Activity> {
    return fetchWithAuth('/activities', {
      method: 'POST',
      body: JSON.stringify(activityData),
    });
  },

  async getTasks(statusFilter?: string): Promise<TaskItem[]> {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return fetchWithAuth(`/activities/tasks${query}`);
  },

  async createTask(taskData: Partial<TaskItem>): Promise<TaskItem> {
    return fetchWithAuth('/activities/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  async toggleTask(taskId: number, is_completed: boolean): Promise<TaskItem> {
    return fetchWithAuth(`/activities/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_completed }),
    });
  },

  async getMeetings(): Promise<MeetingItem[]> {
    return fetchWithAuth('/activities/meetings');
  },

  async createMeeting(meetingData: Partial<MeetingItem>): Promise<MeetingItem> {
    return fetchWithAuth('/activities/meetings', {
      method: 'POST',
      body: JSON.stringify(meetingData),
    });
  },

  // Global Search
  async search(query: string): Promise<Record<string, GlobalSearchResult[]>> {
    return fetchWithAuth(`/search?q=${encodeURIComponent(query)}`);
  },

  // AI Assistant
  async sendAIChat(message: string, contextType?: string, contextId?: number) {
    return fetchWithAuth('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context_type: contextType, context_id: contextId }),
    });
  },

  // Industry Modules
  async getProperties() {
    return fetchWithAuth('/industries/real-estate/properties');
  },
  async getSiteVisits() {
    return fetchWithAuth('/industries/real-estate/site-visits');
  },
  async getCourses() {
    return fetchWithAuth('/industries/edtech/courses');
  },
  async getStudentApplications() {
    return fetchWithAuth('/industries/edtech/applications');
  },
  async getClientPortfolios() {
    return fetchWithAuth('/industries/bfsi/portfolios');
  },
  async getHealthcareAppointments() {
    return fetchWithAuth('/industries/healthcare/appointments');
  },
  async getEcommerceOrders() {
    return fetchWithAuth('/industries/ecommerce/orders');
  },
  async getSaaSProposals() {
    return fetchWithAuth('/industries/b2b-saas/proposals');
  },
  async getSaaSSubscriptions() {
    return fetchWithAuth('/industries/b2b-saas/subscriptions');
  },
};
