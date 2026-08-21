import pytest
from app import app
from config.database import db
from models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create a test user
            u = User(username="testuser", password_hash=generate_password_hash("password123"), role="employee")
            u.id = 1
            db.session.add(u)
            
            u_inactive = User(username="inactive", password_hash=generate_password_hash("pwd"), role="employee", is_active=False)
            u_inactive.id = 2
            db.session.add(u_inactive)
            db.session.commit()
            
            from models.employee import Employee
            emp = Employee(user_id=1, full_name="Test User")
            db.session.add(emp)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_valid_login(client):
    response = client.post("/login", data={
        "username": "testuser",
        "password": "password123"
    }, follow_redirects=True)
    assert b"Expense360" in response.data

def test_invalid_username(client):
    response = client.post("/login", data={
        "username": "wronguser",
        "password": "password123"
    }, follow_redirects=True)
    assert b"Invalid username or password" in response.data

def test_invalid_password(client):
    response = client.post("/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert b"Invalid username or password" in response.data

def test_inactive_user(client):
    response = client.post("/login", data={
        "username": "inactive",
        "password": "pwd"
    }, follow_redirects=True)
    assert b"Account is inactive" in response.data

def test_logout(client):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data
