import pytest
import json
from app import app
from config.database import db
from models.user import User
from models.employee import Employee
from models.expense_claim import ExpenseClaim
from models.travel_request import TravelRequest

@pytest.fixture
def api_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Setup Users
            from werkzeug.security import generate_password_hash
            u_emp = User(username="api_emp", password_hash=generate_password_hash("pwd"), role="employee")
            u_emp2 = User(username="api_emp2", password_hash=generate_password_hash("pwd"), role="employee")
            u_mgr = User(username="api_mgr", password_hash=generate_password_hash("pwd"), role="manager")
            u_fin = User(username="api_fin", password_hash=generate_password_hash("pwd"), role="finance_admin")
            db.session.add_all([u_emp, u_emp2, u_mgr, u_fin])
            db.session.commit()
            
            emp = Employee(user_id=u_emp.id, full_name="API Employee")
            emp2 = Employee(user_id=u_emp2.id, full_name="API Employee 2")
            db.session.add_all([emp, emp2])
            db.session.commit()
            
            from datetime import date
            tr_appr = TravelRequest(employee_id=emp.id, destination="Valid", purpose="Test", travel_date=date(2026,1,1), return_date=date(2026,1,2), status="approved")
            tr_unappr = TravelRequest(employee_id=emp.id, destination="Invalid", purpose="Test", travel_date=date(2026,1,1), return_date=date(2026,1,2), status="pending")
            tr_other = TravelRequest(employee_id=emp2.id, destination="Other", purpose="Test", travel_date=date(2026,1,1), return_date=date(2026,1,2), status="approved")
            db.session.add_all([tr_appr, tr_unappr, tr_other])
            db.session.commit()
            
            c = ExpenseClaim(employee_id=emp.id, title="API Claim", description="Testing", status="submitted")
            c_appr = ExpenseClaim(employee_id=emp.id, title="Appr Claim", description="Test", status="approved")
            c_verif = ExpenseClaim(employee_id=emp.id, title="Verif Claim", description="Test", status="finance_verified")
            db.session.add_all([c, c_appr, c_verif])
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()


def get_auth_headers(client, username, password="pwd"):
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    data = json.loads(res.data)
    return {"Authorization": f"Bearer {data['access_token']}"}


def test_api_missing_jwt(api_client):
    res = api_client.get("/api/claims")
    assert res.status_code == 401

def test_api_invalid_jwt(api_client):
    res = api_client.get("/api/claims", headers={"Authorization": "Bearer invalid_token"})
    assert res.status_code == 422
    
def test_api_unauthenticated(api_client):
    res = api_client.get("/api/claims")
    assert res.status_code == 401

def test_api_unauthorized(api_client):
    headers = get_auth_headers(api_client, "api_mgr")
    res = api_client.post("/api/claims", json={"title": "test", "description": "test"}, headers=headers)
    assert res.status_code == 403  # Manager cannot create claims

def test_api_get_claims(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.get("/api/claims", headers=headers)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert len(data) == 3

def test_api_create_claim(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"title": "New Claim", "description": "Desc"}, headers=headers)
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["title"] == "New Claim"

def test_api_get_nonexistent_resource(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.get("/api/claims/999", headers=headers)
    assert res.status_code == 404

def test_api_validation_failure(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"description": "Missing title"}, headers=headers)
    assert res.status_code == 400

# ── TR Validation Tests ──
def test_create_claim_valid_tr(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"title": "TR Claim", "description": "Desc", "travel_request_id": 1}, headers=headers)
    assert res.status_code == 201

def test_create_claim_nonexistent_tr(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"title": "Claim", "description": "Desc", "travel_request_id": 999}, headers=headers)
    assert res.status_code == 404

def test_create_claim_other_employee_tr(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"title": "Claim", "description": "Desc", "travel_request_id": 3}, headers=headers)
    assert res.status_code == 403

def test_create_claim_unapproved_tr(api_client):
    headers = get_auth_headers(api_client, "api_emp")
    res = api_client.post("/api/claims", json={"title": "Claim", "description": "Desc", "travel_request_id": 2}, headers=headers)
    assert res.status_code == 400

# ── Finance Verification Tests ──
def test_verify_claim_success(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/2/verify", json={"comments": "Looks good"}, headers=headers)
    assert res.status_code == 200

def test_verify_claim_unauthorized(api_client):
    headers = get_auth_headers(api_client, "api_mgr")
    res = api_client.post("/api/claims/2/verify", json={"comments": "Looks good"}, headers=headers)
    assert res.status_code == 403

def test_verify_claim_invalid_state(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/1/verify", json={"comments": "Looks good"}, headers=headers)
    assert res.status_code == 400 # 1 is 'submitted'

def test_verify_claim_duplicate(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/3/verify", json={"comments": "Looks good"}, headers=headers)
    assert res.status_code == 400 # 3 is 'finance_verified'

# ── Finance Reimbursement Tests ──
def test_reimburse_claim_success(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/3/reimburse", json={}, headers=headers)
    assert res.status_code == 200

def test_reimburse_claim_unauthorized(api_client):
    headers = get_auth_headers(api_client, "api_mgr")
    res = api_client.post("/api/claims/3/reimburse", json={}, headers=headers)
    assert res.status_code == 403

def test_reimburse_claim_before_verification(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/2/reimburse", json={}, headers=headers)
    assert res.status_code == 400 # 2 is 'approved'

def test_reimburse_claim_duplicate(api_client):
    headers = get_auth_headers(api_client, "api_fin")
    res = api_client.post("/api/claims/3/reimburse", json={}, headers=headers)
    assert res.status_code == 200
    res2 = api_client.post("/api/claims/3/reimburse", json={}, headers=headers)
    assert res2.status_code == 400
