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
            u_mgr = User(username="api_mgr", password_hash=generate_password_hash("pwd"), role="manager")
            db.session.add_all([u_emp, u_mgr])
            db.session.commit()
            
            emp = Employee(user_id=u_emp.id, full_name="API Employee")
            db.session.add(emp)
            db.session.commit()
            
            from datetime import date
            tr = TravelRequest(employee_id=emp.id, destination="API City", purpose="API Test", travel_date=date(2026,1,1), return_date=date(2026,1,2))
            db.session.add(tr)
            db.session.commit()
            
            c = ExpenseClaim(employee_id=emp.id, title="API Claim", description="Testing", status="submitted")
            db.session.add(c)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_api_unauthenticated(api_client):
    res = api_client.get("/api/claims")
    assert res.status_code == 401

def test_api_unauthorized(api_client):
    api_client.post("/login", data={"username": "api_mgr", "password": "pwd"})
    res = api_client.post("/api/claims", json={"title": "test", "description": "test"})
    assert res.status_code == 403  # Manager cannot create claims

def test_api_get_claims(api_client):
    api_client.post("/login", data={"username": "api_emp", "password": "pwd"})
    res = api_client.get("/api/claims")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert len(data) == 1
    assert data[0]["title"] == "API Claim"

def test_api_create_claim(api_client):
    api_client.post("/login", data={"username": "api_emp", "password": "pwd"})
    res = api_client.post("/api/claims", json={"title": "New Claim", "description": "Desc"})
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["title"] == "New Claim"

def test_api_get_nonexistent_resource(api_client):
    api_client.post("/login", data={"username": "api_emp", "password": "pwd"})
    res = api_client.get("/api/claims/999")
    assert res.status_code == 404

def test_api_validation_failure(api_client):
    api_client.post("/login", data={"username": "api_emp", "password": "pwd"})
    res = api_client.post("/api/claims", json={"description": "Missing title"})
    assert res.status_code == 400
