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
            user_emp1 = User(username="emp1", password_hash=generate_password_hash("pass"), role="employee")
            user_emp1.id = 1
            emp1 = Employee(user_id=1, full_name="Employee One")
            emp1.id = 1
            
            user_emp2 = User(username="emp2", password_hash=generate_password_hash("pass"), role="employee")
            user_emp2.id = 2
            emp2 = Employee(user_id=2, full_name="Employee Two")
            emp2.id = 2
            
            user_mgr = User(username="manager", password_hash=generate_password_hash("pass"), role="manager")
            user_mgr.id = 3
            user_fin = User(username="finance", password_hash=generate_password_hash("pass"), role="finance_admin")
            user_fin.id = 4
            
            db.session.add_all([user_emp1, emp1, user_emp2, emp2, user_mgr, user_fin])
            
            from datetime import date
            
            # Setup claim for emp1
            claim = ExpenseClaim(employee_id=1, title="Emp1 Claim", status="draft", total_amount=100.0)
            claim.id = 1
            item = ExpenseItem(claim_id=1, category_id=1, description="Test", amount=100.0, expense_date=date(2026, 1, 1))
            item.id = 1
            receipt = ExpenseReceipt(item_id=1, filename="test.pdf", file_path="/fake/test.pdf")
            receipt.id = 1
            db.session.add_all([claim, item, receipt])
            
            db.session.commit()
            
            yield client
            db.session.remove()
            db.drop_all()
