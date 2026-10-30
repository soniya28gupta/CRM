# NexusCRM — AI-Powered Customer Relationship Management

> A production-grade, multi-tenant AI CRM web platform with an information-dense enterprise architecture. Built with **Next.js 14+ (App Router)**, **FastAPI**, **SQLAlchemy**, **PostgreSQL / SQLite**, and an **LLM Copilot with strict RBAC backend tools**.

---

## 🚀 Key Highlights & Architecture

- **Multi-Tenant Logical Isolation:** Complete data partitioning across organizations with tenant keys and foreign key constraints on every entity.
- **Enterprise CRM Interface:** Crisp, clean white/slate design system, collapsible 12-section sidebar, quick-create actions, global search (`⌘K`), and high-density tables.
- **AI-Powered CRM Assistant:** Natural-language CRM assistant querying authorized pipeline metrics, high-value deals, upcoming meetings, and overdue tasks via secure backend tools.
- **Transparent AI Lead Scoring:** Automatic 0–100 qualification scoring with factor breakdown (executive authority, lead source, deal value, engagement) and actionable next steps.
- **Interactive Kanban Pipeline:** Configurable 6-stage sales pipeline (`New Lead`, `Contacted`, `Demo`, `Negotiation`, `Won`, `Lost`) with stage probability weighting and revenue metrics.
- **6 Dedicated Industry Modules:**
  1. **Real Estate & Construction:** Properties, Projects, Site Visits, and Bookings.
  2. **EdTech & Training:** Course Catalog, Applications, Demo Classes, and Enrollments.
  3. **BFSI & Finance:** Institutional Portfolios, Document Compliance, and Renewals.
  4. **Healthcare & Clinics:** Healthcare Providers, Patient Consultations, and Follow-ups.
  5. **E-Commerce & D2C:** Customer Orders, Support Tickets, and Abandoned Cart Recovery.
  6. **B2B SaaS:** Annual Proposals, MRR/ARR Subscriptions, and Customer Onboarding.
- **Unified Activity Timeline & Task Engine:** Real-time log of calls, emails, notes, meetings, status changes, and due/overdue follow-ups.

---

## 📂 Project Structure

```
CRM/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py              # RBAC & Tenant dependency resolution
│   │   │   └── routers/             # Auth, Leads, Contacts, Accounts, Deals, Activities, Dashboard, Industries, AI, Search
│   │   ├── core/
│   │   │   ├── config.py            # Environment configurations & CORS
│   │   │   ├── database.py          # SQLAlchemy engine & session factory
│   │   │   └── security.py          # PBKDF2-HMAC password hashing & JWT token sessions
│   │   ├── models/                  # Base, User, Org, CRM, and 6 Industry modules
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── ai_service.py        # Natural language query engine
│   │   │   ├── scoring_service.py   # AI lead scoring algorithm
│   │   │   └── seed_data.py         # Realistic demo seed records
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── tests/
│   │   └── test_crm.py              # Automated Pytest suite
│   ├── run_tests.py                 # Test runner script
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js 14+ App Router routes
│   │   │   ├── (dashboard)/         # Protected CRM shell routes
│   │   │   ├── login/               # Authentication & organization creation
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── layout/              # Sidebar, Topbar, Global Search modal
│   │   │   ├── dashboard/           # MetricCard, Analytics charts
│   │   │   ├── deals/               # Interactive KanbanBoard
│   │   │   ├── leads/               # LeadModal, ConvertLeadModal, LeadScoreModal
│   │   │   ├── common/              # ActivityTimeline
│   │   │   └── ai/                  # AIChatPanel copilot
│   │   ├── lib/
│   │   │   └── api.ts               # Type-safe API client
│   │   └── types/
│   │       └── crm.ts               # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── docker-compose.yml               # PostgreSQL, Backend, and Frontend orchestration
├── .env.example
├── .gitignore
└── README.md
```

---

## Dashboard metric definitions

- **Conversion rate:** leads with status `CONVERTED` divided by all leads in the organization, multiplied by 100. An organization with no leads reports 0%.
- **Open pipeline value:** sum of deal values where status is `OPEN`.
- **Weighted pipeline value:** sum of each `OPEN` deal's value multiplied by its probability divided by 100.
- **Closed-won revenue:** sum of deal values where status is `WON`.
- **Monthly lead trend:** for each of the current and preceding five calendar months, `value` is the count of leads created in that month and `secondary_value` is the count of leads whose `converted_at` falls in that month.
- **Deals by stage:** total value and deal count for each stage belonging to a pipeline in the current organization. It includes open and closed deals.
- Dashboard KPI cards do not claim month-over-month changes because the application does not currently retain historical snapshots for all of those metrics.

All dashboard queries are organization-scoped. The chart endpoints return empty/zero-valued series for organizations without records rather than sample statistics.

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ (Node.js 22 tested)

For Docker, copy `.env.example` to `.env` and replace `POSTGRES_PASSWORD` and `SECRET_KEY` with independent random values before running Compose. Demo seed users are enabled by default for local development and disabled when `APP_ENV=production`.

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Run the backend server (automatically initializes SQLite and seeds demo records)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI documentation will be available at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Open `http://localhost:3000` in your browser.
The browser sends API calls to the same-origin `/api` route; Next.js proxies them to the backend. For Docker Compose, the proxy target is configured as `http://backend:8000`. When building the frontend for another deployment, set `API_INTERNAL_URL` to a backend address reachable by the Next.js server at build time.

---

## 🔑 Pre-Configured Demo Credentials

The local development seed initializes realistic synthetic data on first startup. Do not enable demo seeding for a production deployment:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@crm.io` | `admin123` | Full administrative & organization access |
| **Sales Rep** | `alex.sales@crm.io` | `sales123` | Pipeline management, lead qualification & activity logging |
| **Viewer** | `m.vance@apexhealth.org` | `admin123` | Read-only access to organization records |

---

## 🧪 Automated Testing

Run the full backend test suite verifying authentication, lead qualification, deal movements, organization isolation, and AI query tool calls:
```bash
python backend/run_tests.py
```
Expected output:
```
backend/tests/test_crm.py::test_health_check PASSED                      [ 16%]
backend/tests/test_crm.py::test_login_success PASSED                     [ 33%]
backend/tests/test_crm.py::test_login_failure PASSED                     [ 50%]
backend/tests/test_crm.py::test_leads_crud_and_scoring PASSED            [ 66%]
backend/tests/test_crm.py::test_kanban_and_stage_movement PASSED         [ 83%]
backend/tests/test_crm.py::test_ai_crm_chat PASSED                       [100%]
======================= 6 passed in 2.37s =======================
```

---

## 🚢 Deployment

### Production Docker Orchestration
```bash
docker-compose up --build
```
This spins up:
- Managed PostgreSQL on port `5432`
- FastAPI API server on port `8000`
- Next.js Production Web App on port `3000`

### Vercel & Render Deployment
- **Frontend (Vercel):** Connect GitHub repo, set root directory to `frontend`, and configure `NEXT_PUBLIC_API_URL` to your production backend URL.
- **Backend (Render / Railway):** Connect GitHub repo, set root directory to `backend`, set start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and set `DATABASE_URL` to your managed PostgreSQL connection string.
