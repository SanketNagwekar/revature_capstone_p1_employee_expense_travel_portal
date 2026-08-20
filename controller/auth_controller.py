from flask import Blueprint, request, render_template, redirect, session
from service.auth_service import AuthService
from dao.user_dao import UserDAO

auth_controller = Blueprint("auth_controller", __name__)

auth_service = AuthService(UserDAO())

ROLE_DASHBOARD = {
    "employee":      "/employee/dashboard",
    "manager":       "/manager/dashboard",
    "finance_admin": "/finance/dashboard",
    "system_admin":  "/admin/dashboard"
}

@auth_controller.route("/", methods=["GET"])
def home():
    if "user_id" in session:
        return redirect(ROLE_DASHBOARD.get(session["role"], "/login"))
    return redirect("/login")

@auth_controller.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(ROLE_DASHBOARD.get(session["role"], "/login"))

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    try:
        user = auth_service.login(username, password)
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role
        if user.employee:
            session["employee_id"] = user.employee.id
        return redirect(ROLE_DASHBOARD.get(user.role, "/login"))
    except ValueError as e:
        return render_template("login.html", error=str(e))

@auth_controller.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
