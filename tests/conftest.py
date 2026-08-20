import pytest
import os
os.environ["DB_USERNAME"] = ""
os.environ["DB_PASSWORD"] = ""
os.environ["DB_HOST"] = ""
os.environ["DB_NAME"] = ""

from app import app
from config.database import db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["WTF_CSRF_ENABLED"] = False

# Force Flask-SQLAlchemy to reinitialize and use sqlite
if "sqlalchemy" in app.extensions:
    del app.extensions["sqlalchemy"]
db.init_app(app)

@pytest.fixture
def test_client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            from models.user import User
            from models.employee import Employee
            from models.expense_claim import ExpenseClaim
            from models.expense_item import ExpenseItem
            from models.expense_receipt import ExpenseReceipt
            from werkzeug.security import generate_password_hash
            
            # Setup users
            user_emp1 = User(id=1, username="emp1", password_hash=generate_password_hash("pass"), role="employee")
            emp1 = Employee(id=1, user_id=1, full_name="Employee One")
            
            user_emp2 = User(id=2, username="emp2", password_hash=generate_password_hash("pass"), role="employee")
            emp2 = Employee(id=2, user_id=2, full_name="Employee Two")
            
            user_mgr = User(id=3, username="manager", password_hash=generate_password_hash("pass"), role="manager")
            user_fin = User(id=4, username="finance", password_hash=generate_password_hash("pass"), role="finance_admin")
            
            db.session.add_all([user_emp1, emp1, user_emp2, emp2, user_mgr, user_fin])
            
            from datetime import date
            
            # Setup claim for emp1
            claim = ExpenseClaim(id=1, employee_id=1, title="Emp1 Claim", status="draft", total_amount=100.0)
            item = ExpenseItem(id=1, claim_id=1, category_id=1, description="Test", amount=100.0, expense_date=date(2026, 1, 1))
            receipt = ExpenseReceipt(id=1, item_id=1, filename="test.pdf", file_path="/fake/test.pdf")
            db.session.add_all([claim, item, receipt])
            
            db.session.commit()
            
            yield client
            db.drop_all()
