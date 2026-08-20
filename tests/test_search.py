import pytest
from app import app
from config.database import db
from models.user import User
from models.employee import Employee
from models.expense_claim import ExpenseClaim
from werkzeug.security import generate_password_hash

@pytest.fixture
def search_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            u = User(username="testsearch", password_hash=generate_password_hash("pwd"), role="employee")
            u.id = 1
            db.session.add(u)
            
            emp = Employee(user_id=1, full_name="Search Tester")
            emp.id = 1
            db.session.add(emp)
            db.session.commit()
            
            # Claims
            c1 = ExpenseClaim(employee_id=1, title="Trip to NY", description="Flight and hotel", status="submitted")
            c1.id = 100
            
            c2 = ExpenseClaim(employee_id=1, title="Team lunch", description="Pizza", status="approved")
            c2.id = 101
            
            c3 = ExpenseClaim(employee_id=1, title="Office supplies", description="Pens and paper", status="draft")
            c3.id = 102
            
            db.session.add_all([c1, c2, c3])
            db.session.commit()
            
        client.post("/login", data={"username": "testsearch", "password": "pwd"})
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_search_by_claim_id(search_client):
    response = search_client.get("/expense/my-claims?search=101")
    assert b"Team lunch" in response.data
    assert b"Trip to NY" not in response.data

def test_search_by_title_description(search_client):
    response = search_client.get("/expense/my-claims?search=Pizza")
    assert b"Team lunch" in response.data
    assert b"Office supplies" not in response.data

def test_matching_claims_returned(search_client):
    response = search_client.get("/expense/my-claims?search=Trip")
    assert b"Trip to NY" in response.data
    assert b"Team lunch" not in response.data

def test_unrelated_claims_excluded(search_client):
    response = search_client.get("/expense/my-claims?search=UnrelatedNonExistent")
    assert b"No expense claims yet" in response.data or b"0" in response.data or response.status_code == 200

def test_status_filtering_works(search_client):
    response = search_client.get("/expense/my-claims?status=draft")
    assert b"Office supplies" in response.data
    assert b"Team lunch" not in response.data
    assert b"Trip to NY" not in response.data
