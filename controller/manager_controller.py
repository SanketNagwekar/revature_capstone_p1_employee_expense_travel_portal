from flask import Blueprint, request, render_template, redirect, session
from service.expense_service import ExpenseService
from service.travel_service import TravelService
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.expense_item_dao import ExpenseItemDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from dao.expense_receipt_dao import ExpenseReceiptDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from dao.travel_request_dao import TravelRequestDAO
from dao.expense_category_dao import ExpenseCategoryDAO
from utils import role_required

manager_controller = Blueprint("manager_controller", __name__, url_prefix="/manager")

expense_service = ExpenseService(
    ExpenseClaimDAO(), ExpenseItemDAO(),
    ExpensePolicyDAO(), ExpenseReceiptDAO(), ApprovalHistoryDAO()
)
travel_service = TravelService(TravelRequestDAO())
category_dao = ExpenseCategoryDAO()

@manager_controller.route("/dashboard")
@role_required("manager")
def dashboard():
    pending_claims = expense_service.get_by_status("submitted")
    pending_travel = travel_service.get_pending()
    return render_template(
        "manager/dashboard.html",
        pending_claims=pending_claims,
        pending_travel=pending_travel
    )

# ── Expense Claim Actions ──
@manager_controller.route("/claims/<int:claim_id>")
@role_required("manager")
def view_claim(claim_id):
    try:
        claim = expense_service.get_by_id(claim_id)
    except ValueError:
        return redirect("/manager/dashboard")
    categories = category_dao.get_all()
    history = expense_service.get_history(claim_id)
    return render_template("manager/claim_review.html", claim=claim, categories=categories, history=history)

@manager_controller.route("/claims/<int:claim_id>/approve", methods=["POST"])
@role_required("manager")
def approve_claim(claim_id):
    comments = request.form.get("comments", "")
    try:
        expense_service.approve_claim(claim_id, session.get("user_id"), comments)
    except ValueError as e:
        pending_claims = expense_service.get_by_status("submitted")
        pending_travel = travel_service.get_pending()
        return render_template("manager/dashboard.html", pending_claims=pending_claims, pending_travel=pending_travel, error=str(e))
    return redirect("/manager/dashboard")

@manager_controller.route("/claims/<int:claim_id>/reject", methods=["POST"])
@role_required("manager")
def reject_claim(claim_id):
    comments = request.form.get("comments", "")
    try:
        expense_service.reject_claim(claim_id, session.get("user_id"), comments)
    except ValueError as e:
        pending_claims = expense_service.get_by_status("submitted")
        pending_travel = travel_service.get_pending()
        return render_template("manager/dashboard.html", pending_claims=pending_claims, pending_travel=pending_travel, error=str(e))
    return redirect("/manager/dashboard")

# ── Travel Request Actions ──
@manager_controller.route("/travel/<int:request_id>/approve", methods=["POST"])
@role_required("manager")
def approve_travel(request_id):
    try:
        travel_service.approve(request_id)
    except ValueError:
        pass
    return redirect("/manager/dashboard")

@manager_controller.route("/travel/<int:request_id>/reject", methods=["POST"])
@role_required("manager")
def reject_travel(request_id):
    try:
        travel_service.reject(request_id)
    except ValueError:
        pass
    return redirect("/manager/dashboard")
