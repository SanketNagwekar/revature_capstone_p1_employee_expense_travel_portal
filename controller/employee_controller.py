from flask import Blueprint, render_template, session
from service.employee_service import EmployeeService
from service.travel_service import TravelService
from service.expense_service import ExpenseService
from dao.employee_dao import EmployeeDAO
from dao.travel_request_dao import TravelRequestDAO
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.expense_item_dao import ExpenseItemDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from dao.expense_receipt_dao import ExpenseReceiptDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from utils import role_required

employee_controller = Blueprint("employee_controller", __name__, url_prefix="/employee")

employee_service = EmployeeService(EmployeeDAO())
travel_service = TravelService(TravelRequestDAO())
expense_service = ExpenseService(
    ExpenseClaimDAO(), ExpenseItemDAO(),
    ExpensePolicyDAO(), ExpenseReceiptDAO(), ApprovalHistoryDAO()
)

@employee_controller.route("/dashboard")
@role_required("employee")
def dashboard():
    employee_id = session.get("employee_id")
    employee = employee_service.get_by_id(employee_id)
    travel_requests = travel_service.get_by_employee(employee_id)
    claims = expense_service.get_by_employee(employee_id)

    stats = {
        "travel_pending":   sum(1 for t in travel_requests if t.status == "pending"),
        "travel_approved":  sum(1 for t in travel_requests if t.status == "approved"),
        "claims_submitted": sum(1 for c in claims if c.status == "submitted"),
        "claims_approved":  sum(1 for c in claims if c.status == "approved"),
        "reimbursed":       sum(1 for c in claims if c.status == "reimbursed"),
    }
    recent_travel = travel_requests[:5]
    recent_claims = claims[:5]
    return render_template(
        "employee/dashboard.html",
        employee=employee,
        stats=stats,
        recent_travel=recent_travel,
        recent_claims=recent_claims
    )
