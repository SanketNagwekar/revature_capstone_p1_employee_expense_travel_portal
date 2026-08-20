from flask import Blueprint, request, render_template, redirect, session
from service.admin_service import AdminService
from dao.user_dao import UserDAO
from dao.employee_dao import EmployeeDAO
from dao.expense_category_dao import ExpenseCategoryDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from utils import role_required

admin_controller = Blueprint("admin_controller", __name__, url_prefix="/admin")

admin_service = AdminService(UserDAO(), EmployeeDAO(), ExpenseCategoryDAO(), ExpensePolicyDAO())

@admin_controller.route("/dashboard")
@role_required("system_admin")
def dashboard():
    users = admin_service.get_all_users()
    categories = admin_service.get_all_categories()
    policies = admin_service.get_all_policies()
    return render_template("admin/dashboard.html", users=users, categories=categories, policies=policies)

# ── User routes ──
@admin_controller.route("/users/add", methods=["POST"])
@role_required("system_admin")
def add_user():
    data = request.form
    try:
        admin_service.create_user(
            username=data.get("username"),
            password=data.get("password"),
            role=data.get("role"),
            full_name=data.get("full_name"),
            department=data.get("department"),
            designation=data.get("designation"),
            phone=data.get("phone")
        )
    except ValueError as e:
        users = admin_service.get_all_users()
        categories = admin_service.get_all_categories()
        policies = admin_service.get_all_policies()
        return render_template("admin/dashboard.html", users=users, categories=categories, policies=policies, user_error=str(e))
    return redirect("/admin/dashboard")

@admin_controller.route("/users/<int:user_id>/toggle", methods=["POST"])
@role_required("system_admin")
def toggle_user(user_id):
    try:
        admin_service.toggle_user_active(user_id)
    except ValueError:
        pass
    return redirect("/admin/dashboard")

@admin_controller.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("system_admin")
def delete_user(user_id):
    try:
        admin_service.delete_user(user_id)
    except ValueError:
        pass
    return redirect("/admin/dashboard")

# ── Category routes ──
@admin_controller.route("/categories/add", methods=["POST"])
@role_required("system_admin")
def add_category():
    try:
        admin_service.create_category(
            name=request.form.get("name"),
            description=request.form.get("description")
        )
    except ValueError as e:
        users = admin_service.get_all_users()
        categories = admin_service.get_all_categories()
        policies = admin_service.get_all_policies()
        return render_template("admin/dashboard.html", users=users, categories=categories, policies=policies, cat_error=str(e))
    return redirect("/admin/dashboard")

@admin_controller.route("/categories/<int:cat_id>/delete", methods=["POST"])
@role_required("system_admin")
def delete_category(cat_id):
    try:
        admin_service.delete_category(cat_id)
    except ValueError:
        pass
    return redirect("/admin/dashboard")

# ── Policy routes ──
@admin_controller.route("/policies/add", methods=["POST"])
@role_required("system_admin")
def add_policy():
    try:
        admin_service.create_policy(
            category_id=request.form.get("category_id"),
            max_amount=float(request.form.get("max_amount")),
            description=request.form.get("description")
        )
    except ValueError as e:
        users = admin_service.get_all_users()
        categories = admin_service.get_all_categories()
        policies = admin_service.get_all_policies()
        return render_template("admin/dashboard.html", users=users, categories=categories, policies=policies, policy_error=str(e))
    return redirect("/admin/dashboard")

@admin_controller.route("/policies/<int:policy_id>/update", methods=["POST"])
@role_required("system_admin")
def update_policy(policy_id):
    try:
        admin_service.update_policy(
            policy_id=policy_id,
            max_amount=float(request.form.get("max_amount")),
            description=request.form.get("description")
        )
    except ValueError:
        pass
    return redirect("/admin/dashboard")

@admin_controller.route("/policies/<int:policy_id>/delete", methods=["POST"])
@role_required("system_admin")
def delete_policy(policy_id):
    try:
        admin_service.delete_policy(policy_id)
    except ValueError:
        pass
    return redirect("/admin/dashboard")
