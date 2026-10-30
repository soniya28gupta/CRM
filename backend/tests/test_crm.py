import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.services.seed_data import seed_database_if_empty
from app.core.security import create_access_token

# In-memory SQLite with StaticPool so all connections share the same memory database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database_if_empty(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@crm.io"
    assert data["user"]["role"] == "ADMIN"

def test_session_status_does_not_error_for_anonymous_or_authenticated_user(client):
    anonymous_response = client.get("/api/auth/session")
    assert anonymous_response.status_code == 200
    assert anonymous_response.json() == {"authenticated": False}

    login_response = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123"
    })
    assert login_response.status_code == 200

    session_response = client.get("/api/auth/session")
    assert session_response.status_code == 200
    assert session_response.json() == {"authenticated": True}

def test_login_failure(client):
    response = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_invalid_and_expired_tokens_are_rejected(client):
    expired_token = create_access_token({"sub": "1"}, expires_delta_seconds=-1)
    expired_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired_response.status_code == 401

    invalid_response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert invalid_response.status_code == 401

def test_leads_crud_and_scoring(client):
    # 1. Login
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Leads list
    leads_resp = client.get("/api/leads", headers=headers)
    assert leads_resp.status_code == 200
    data = leads_resp.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0

    # 3. Create new Lead
    new_lead = {
        "first_name": "Elon",
        "last_name": "Tusk",
        "email": "elontusk@starorbital.com",
        "company": "StarOrbital Aerospace",
        "job_title": "Chief Technology Officer",
        "lead_source": "LinkedIn",
        "industry": "Technology",
        "status": "NEW",
        "priority": "HIGH",
        "estimated_value": 75000.0,
        "notes": "Interested in enterprise orbital telemetry API."
    }
    create_resp = client.post("/api/leads", json=new_lead, headers=headers)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["first_name"] == "Elon"
    assert created["lead_score"] >= 70

    # 4. Score explanation
    score_resp = client.post(f"/api/leads/{created['id']}/score", headers=headers)
    assert score_resp.status_code == 200
    score_data = score_resp.json()
    assert "factors" in score_data
    assert len(score_data["factors"]) > 0

    # 5. Convert lead to Deal and Account
    convert_resp = client.post(f"/api/leads/{created['id']}/convert", json={
        "create_account": True,
        "account_name": "StarOrbital Aerospace Inc",
        "create_deal": True,
        "deal_name": "StarOrbital Orbital Telemetry Contract",
        "deal_value": 75000.0
    }, headers=headers)
    assert convert_resp.status_code == 200
    assert "deal_id" in convert_resp.json()

def test_kanban_and_stage_movement(client):
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    kanban_resp = client.get("/api/deals/kanban", headers=headers)
    assert kanban_resp.status_code == 200
    board = kanban_resp.json()
    assert len(board["columns"]) == 6  # 6 standard stages

    # Move first deal to stage 4 (Negotiation)
    deals = client.get("/api/deals", headers=headers).json()
    deal_to_move = deals[0]
    stages = client.get("/api/deals/pipelines", headers=headers).json()[0]["stages"]
    target_stage = stages[3]

    move_resp = client.patch(
        f"/api/deals/{deal_to_move['id']}/stage",
        json={"stage_id": target_stage["id"]},
        headers=headers
    )
    assert move_resp.status_code == 200
    assert move_resp.json()["stage_id"] == target_stage["id"]

    update_resp = client.patch(
        f"/api/deals/{deal_to_move['id']}",
        json={"name": "Updated pipeline opportunity", "value": 12345.0},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated pipeline opportunity"
    assert update_resp.json()["value"] == 12345.0

def test_ai_crm_chat(client):
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    query_resp = client.post("/api/ai/chat", json={
        "message": "Which open deals have the highest value?"
    }, headers=headers)
    assert query_resp.status_code == 200
    ai_data = query_resp.json()
    assert "reply" in ai_data
    assert len(ai_data["suggested_actions"]) > 0


def test_tenant_references_and_dashboard_are_isolated(client):
    registration = client.post("/api/auth/register", json={
        "email": "isolation-test@example.com",
        "password": "secure-test-password",
        "full_name": "Isolation Test",
        "organization_name": "Isolation Test Organization",
    })
    assert registration.status_code == 200
    tenant_token = registration.json()["access_token"]
    tenant_headers = {"Authorization": f"Bearer {tenant_token}"}
    foreign_user_id = registration.json()["user"]["id"]

    account_response = client.post(
        "/api/accounts",
        json={"name": "Private Tenant Account"},
        headers=tenant_headers,
    )
    assert account_response.status_code == 200
    foreign_account_id = account_response.json()["id"]
    course_response = client.post(
        "/api/industries/edtech/courses",
        json={"title": "Private Tenant Course"},
        headers=tenant_headers,
    )
    assert course_response.status_code == 200
    property_response = client.post(
        "/api/industries/real-estate/properties",
        json={"title": "Private Tenant Property", "price": 250000, "location": "Test City"},
        headers=tenant_headers,
    )
    assert property_response.status_code == 200

    admin_login = client.post("/api/auth/login", json={
        "email": "admin@crm.io",
        "password": "admin123",
    })
    admin_headers = {
        "Authorization": f"Bearer {admin_login.json()['access_token']}"
    }

    contact_response = client.post(
        "/api/contacts",
        json={
            "first_name": "Cross",
            "last_name": "Tenant",
            "email": "cross-tenant@example.com",
            "account_id": foreign_account_id,
        },
        headers=admin_headers,
    )
    assert contact_response.status_code == 404

    activity_response = client.post(
        "/api/activities",
        json={
            "activity_type": "NOTE",
            "subject": "Cross-tenant note",
            "entity_type": "account",
            "entity_id": foreign_account_id,
        },
        headers=admin_headers,
    )
    assert activity_response.status_code == 404

    lead_response = client.post(
        "/api/leads",
        json={
            "first_name": "Cross",
            "last_name": "Tenant",
            "email": "cross-tenant-lead@example.com",
            "assigned_to_id": foreign_user_id,
        },
        headers=admin_headers,
    )
    assert lead_response.status_code == 404

    foreign_pipeline = client.get("/api/deals/pipelines", headers=tenant_headers).json()[0]
    foreign_stage_id = foreign_pipeline["stages"][0]["id"]
    deal_response = client.post(
        "/api/deals",
        json={
            "name": "Cross-tenant deal",
            "pipeline_id": foreign_pipeline["id"],
            "stage_id": foreign_stage_id,
        },
        headers=admin_headers,
    )
    assert deal_response.status_code == 404
    kanban_response = client.get(
        f"/api/deals/kanban?pipeline_id={foreign_pipeline['id']}",
        headers=admin_headers,
    )
    assert kanban_response.status_code == 404

    application_response = client.post(
        "/api/industries/edtech/applications",
        json={
            "course_id": course_response.json()["id"],
            "applicant_name": "Cross Tenant",
            "applicant_email": "cross-tenant-applicant@example.com",
            "applicant_phone": "+1 555 0100",
        },
        headers=admin_headers,
    )
    assert application_response.status_code == 404
    site_visit_response = client.post(
        "/api/industries/real-estate/site-visits",
        json={
            "property_id": property_response.json()["id"],
            "visitor_name": "Cross Tenant",
            "visitor_phone": "+1 555 0100",
            "scheduled_at": "2026-11-01T10:00:00",
        },
        headers=admin_headers,
    )
    assert site_visit_response.status_code == 404

    charts_response = client.get("/api/dashboard/charts", headers=tenant_headers)
    assert charts_response.status_code == 200
    charts = charts_response.json()
    assert len(charts["monthly_trend"]) == 6
    assert all(point["value"] == 0 for point in charts["monthly_trend"])
    assert all(point["secondary_value"] == 0 for point in charts["monthly_trend"])
    assert len(charts["deals_by_stage"]) == 6
    assert all(point["value"] == 0 for point in charts["deals_by_stage"])
    metrics_response = client.get("/api/dashboard/metrics", headers=tenant_headers)
    assert metrics_response.status_code == 200
    assert all(
        card["change_percentage"] is None
        for card in metrics_response.json()["cards"]
    )
