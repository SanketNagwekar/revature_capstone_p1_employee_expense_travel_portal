from werkzeug.security import generate_password_hash
from models.user import User
from models.employee import Employee
from models.expense_category import ExpenseCategory
from models.expense_policy import ExpensePolicy

class AdminService:
    def __init__(self, user_dao, employee_dao, category_dao, policy_dao):
        self.user_dao = user_dao
        self.employee_dao = employee_dao
        self.category_dao = category_dao
        self.policy_dao = policy_dao

    # ── User management ──
    def get_all_users(self):
        return self.user_dao.get_all()

    def create_user(self, username, password, role, full_name, department, designation, phone):
        if self.user_dao.get_by_username(username):
            raise ValueError("Username already exists")
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        saved_user = self.user_dao.save(user)
        if role == "employee":
            emp = Employee(
                user_id=saved_user.id,
                full_name=full_name,
                department=department,
                designation=designation,
                phone=phone
            )
            self.employee_dao.save(emp)
        return saved_user

    def toggle_user_active(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        user.is_active = not user.is_active
        self.user_dao.save(user)
        return user

    def delete_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        self.user_dao.delete(user)

    # ── Category management ──
    def get_all_categories(self):
        return self.category_dao.get_all()

    def create_category(self, name, description):
        if self.category_dao.get_by_name(name):
            raise ValueError("Category already exists")
        cat = ExpenseCategory(name=name, description=description)
        return self.category_dao.save(cat)

    def delete_category(self, cat_id):
        cat = self.category_dao.get_by_id(cat_id)
        if cat is None:
            raise ValueError("Category not found")
        self.category_dao.delete(cat)

    # ── Policy management ──
    def get_all_policies(self):
        return self.policy_dao.get_all()

    def create_policy(self, category_id, max_amount, description):
        if self.policy_dao.get_by_category(category_id):
            raise ValueError("Policy already exists for this category")
        policy = ExpensePolicy(category_id=category_id, max_amount=max_amount, description=description)
        return self.policy_dao.save(policy)

    def update_policy(self, policy_id, max_amount, description):
        policy = self.policy_dao.get_by_id(policy_id)
        if policy is None:
            raise ValueError("Policy not found")
        policy.max_amount = max_amount
        policy.description = description
        return self.policy_dao.save(policy)

    def delete_policy(self, policy_id):
        policy = self.policy_dao.get_by_id(policy_id)
        if policy is None:
            raise ValueError("Policy not found")
        self.policy_dao.delete(policy)
