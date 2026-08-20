from app import app
from config.database import db
from werkzeug.security import generate_password_hash
from models.user import User
from models.employee import Employee
from models.expense_category import ExpenseCategory
from models.expense_policy import ExpensePolicy

with app.app_context():
    db.create_all()

    # Seed users
    users_data = [
        {"username": "admin",   "password": "admin123",   "role": "system_admin"},
        {"username": "manager", "password": "manager123", "role": "manager"},
        {"username": "finance", "password": "finance123", "role": "finance_admin"},
        {"username": "emp1",    "password": "emp123",     "role": "employee"},
    ]

    created_users = {}
    for ud in users_data:
        if not User.query.filter_by(username=ud["username"]).first():
            u = User(username=ud["username"], password_hash=generate_password_hash(ud["password"]), role=ud["role"])
            db.session.add(u)
            db.session.flush()
            created_users[ud["username"]] = u
            print(f"Created user: {ud['username']} ({ud['role']})")

    db.session.commit()

    # Seed employee profile for emp1
    emp_user = User.query.filter_by(username="emp1").first()
    if emp_user and not Employee.query.filter_by(user_id=emp_user.id).first():
        emp = Employee(user_id=emp_user.id, full_name="John Doe", department="Engineering", designation="Software Engineer", phone="9876543210")
        db.session.add(emp)
        db.session.commit()
        print("Created employee profile for emp1")

    # Seed expense categories
    categories = [
        {"name": "Accommodation", "description": "Hotel and lodging expenses"},
        {"name": "Transportation", "description": "Local travel - cab, bus, train"},
        {"name": "Meals",          "description": "Food and beverage expenses"},
        {"name": "Flight",         "description": "Airfare expenses"},
        {"name": "Other",          "description": "Other business expenses"},
    ]
    for cat in categories:
        if not ExpenseCategory.query.filter_by(name=cat["name"]).first():
            c = ExpenseCategory(name=cat["name"], description=cat["description"])
            db.session.add(c)
            print(f"Created category: {cat['name']}")
    db.session.commit()

    # Seed expense policies (max amount per category)
    policies = {
        "Accommodation": 5000.0,
        "Transportation": 1500.0,
        "Meals":          800.0,
        "Flight":         15000.0,
        "Other":          2000.0,
    }
    for cat_name, max_amt in policies.items():
        cat = ExpenseCategory.query.filter_by(name=cat_name).first()
        if cat and not ExpensePolicy.query.filter_by(category_id=cat.id).first():
            p = ExpensePolicy(category_id=cat.id, max_amount=max_amt, description=f"Max {max_amt} per claim for {cat_name}")
            db.session.add(p)
            print(f"Created policy: {cat_name} -> max {max_amt}")
    db.session.commit()

    print("\nSeed complete.")
