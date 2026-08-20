from flask import Blueprint, request, render_template, redirect, session
from service.expense_service import ExpenseService
from service.travel_service import TravelService
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.expense_item_dao import ExpenseItemDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from dao.expense_receipt_dao import ExpenseReceiptDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from dao.expense_category_dao import ExpenseCategoryDAO
from dao.travel_request_dao import TravelRequestDAO
from utils import role_required
from datetime import datetime

expense_controller = Blueprint("expense_controller", __name__, url_prefix="/expense")

expense_service = ExpenseService(
    ExpenseClaimDAO(), ExpenseItemDAO(),
    ExpensePolicyDAO(), ExpenseReceiptDAO(), ApprovalHistoryDAO()
)
travel_service = TravelService(TravelRequestDAO())
category_dao = ExpenseCategoryDAO()

@expense_controller.route("/new", methods=["GET", "POST"])
@role_required("employee")
def new_claim():
    employee_id = session.get("employee_id")
    approved_travels = [t for t in travel_service.get_by_employee(employee_id) if t.status == "approved"]

    if request.method == "GET":
        return render_template("employee/expense_submission.html", travels=approved_travels)

    try:
        travel_id = request.form.get("travel_request_id")
        claim = expense_service.create_claim(
            employee_id=employee_id,
            title=request.form.get("title"),
            description=request.form.get("description"),
            travel_request_id=int(travel_id) if travel_id else None
        )
        return redirect(f"/expense/{claim.id}")
    except ValueError as e:
        return render_template("employee/expense_submission.html", travels=approved_travels, error=str(e))

@expense_controller.route("/my-claims")
@role_required("employee")
def my_claims():
    employee_id = session.get("employee_id")
    status_filter = request.args.get("status", "")
    all_claims = expense_service.get_by_employee(employee_id)
    if status_filter:
        all_claims = [c for c in all_claims if c.status == status_filter]
    return render_template("employee/my_claims.html", claims=all_claims, status_filter=status_filter)

@expense_controller.route("/<int:claim_id>", methods=["GET"])
@role_required("employee")
def claim_details(claim_id):
    try:
        claim = expense_service.get_by_id(claim_id)
        if claim.employee_id != session.get("employee_id"):
            return redirect("/employee/dashboard")
    except ValueError:
        return redirect("/expense/my-claims")

    categories = category_dao.get_all()
    history = expense_service.get_history(claim_id)
    return render_template("employee/claim_details.html", claim=claim, categories=categories, history=history)

@expense_controller.route("/<int:claim_id>/add-item", methods=["POST"])
@role_required("employee")
def add_item(claim_id):
    try:
        expense_date = datetime.strptime(request.form.get("expense_date"), "%Y-%m-%d").date()
        expense_service.add_item(
            claim_id=claim_id,
            category_id=int(request.form.get("category_id")),
            description=request.form.get("description"),
            amount=float(request.form.get("amount")),
            expense_date=expense_date
        )
    except ValueError as e:
        claim = expense_service.get_by_id(claim_id)
        categories = category_dao.get_all()
        history = expense_service.get_history(claim_id)
        return render_template("employee/claim_details.html", claim=claim, categories=categories, history=history, item_error=str(e))
    return redirect(f"/expense/{claim_id}")

@expense_controller.route("/<int:claim_id>/delete-item/<int:item_id>", methods=["POST"])
@role_required("employee")
def delete_item(claim_id, item_id):
    try:
        expense_service.delete_item(item_id)
    except ValueError:
        pass
    return redirect(f"/expense/{claim_id}")

@expense_controller.route("/<int:claim_id>/submit", methods=["POST"])
@role_required("employee")
def submit_claim(claim_id):
    try:
        expense_service.submit_claim(claim_id, session.get("employee_id"))
    except ValueError as e:
        claim = expense_service.get_by_id(claim_id)
        categories = category_dao.get_all()
        history = expense_service.get_history(claim_id)
        return render_template("employee/claim_details.html", claim=claim, categories=categories, history=history, submit_error=str(e))
    return redirect("/expense/my-claims")
