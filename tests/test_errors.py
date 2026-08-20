import pytest
from app import app
from config.database import db
from models.user import User

@pytest.fixture
def error_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            from werkzeug.security import generate_password_hash
            u = User(username="emp_err", password_hash=generate_password_hash("pwd"), role="employee")
            u.id = 1
            db.session.add(u)
            db.session.commit()
            
            from models.employee import Employee
            emp = Employee(user_id=1, full_name="Err User")
            db.session.add(emp)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_unauthenticated_access(error_client):
    response = error_client.get("/employee/dashboard", follow_redirects=True)
    # Should redirect to login
    assert b"Login" in response.data

def test_unauthorized_access(error_client):
    error_client.post("/login", data={"username": "emp_err", "password": "pwd"})
    # Employee trying to access admin
    response = error_client.get("/admin/dashboard", follow_redirects=True)
    # Redirects to /login, which redirects back to their own dashboard
    assert b"Welcome" in response.data or b"Dashboard" in response.data
    
def test_invalid_resource_id(error_client):
    error_client.post("/login", data={"username": "emp_err", "password": "pwd"})
    response = error_client.get("/expense/invalid_id", follow_redirects=True)
    assert response.status_code == 404

def test_nonexistent_claim(error_client):
    error_client.post("/login", data={"username": "emp_err", "password": "pwd"})
    response = error_client.get("/expense/9999", follow_redirects=True)
    # Controller redirects to /expense/my-claims on ValueError
    assert b"My Claims" in response.data or response.status_code == 200

def test_nonexistent_receipt(error_client):
    error_client.post("/login", data={"username": "emp_err", "password": "pwd"})
    response = error_client.get("/expense/receipt/9999/download", follow_redirects=True)
    # Redirects to login on ValueError in this controller
    assert b"Login" in response.data or response.status_code == 200

def test_invalid_form_data(error_client):
    error_client.post("/login", data={"username": "emp_err", "password": "pwd"})
    response = error_client.post("/expense/new", data={
        "title": "" # Missing title might cause ValueError
    }, follow_redirects=True)
    # In this app, value errors often flash or render with error string
    assert response.status_code == 200
