import pytest
from app import app
from config.database import db
from models.expense_category import ExpenseCategory
from dao.expense_category_dao import ExpenseCategoryDAO

@pytest.fixture
def db_context():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()

def test_create_record(db_context):
    dao = ExpenseCategoryDAO()
    cat = ExpenseCategory(name="TestCat", description="Test")
    saved = dao.save(cat)
    assert saved.id is not None
    assert saved.name == "TestCat"

def test_retrieve_record(db_context):
    dao = ExpenseCategoryDAO()
    cat = ExpenseCategory(name="TestCat", description="Test")
    dao.save(cat)
    
    retrieved = dao.get_by_id(cat.id)
    assert retrieved is not None
    assert retrieved.name == "TestCat"

def test_update_record(db_context):
    dao = ExpenseCategoryDAO()
    cat = ExpenseCategory(name="TestCat", description="Test")
    dao.save(cat)
    
    cat.name = "UpdatedCat"
    dao.save(cat)
    
    retrieved = dao.get_by_id(cat.id)
    assert retrieved.name == "UpdatedCat"

def test_delete_record(db_context):
    dao = ExpenseCategoryDAO()
    cat = ExpenseCategory(name="TestCat", description="Test")
    dao.save(cat)
    
    cat_id = cat.id
    dao.delete(cat)
    
    retrieved = dao.get_by_id(cat_id)
    assert retrieved is None

def test_relationship_persistence(db_context):
    from models.user import User
    from models.employee import Employee
    
    u = User(username="reluser", password_hash="pwd", role="employee")
    u.id = 1
    db.session.add(u)
    
    emp = Employee(user_id=1, full_name="Rel Employee")
    emp.id = 1
    db.session.add(emp)
    db.session.commit()
    
    # Reload and test relationship
    u_reloaded = User.query.get(1)
    assert u_reloaded.employee is not None
    assert u_reloaded.employee.full_name == "Rel Employee"
