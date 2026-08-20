from flask import Blueprint, request, render_template, redirect, session
from service.finance_service import FinanceService
from service.expense_service import ExpenseService
from dao.reimbursement_dao import ReimbursementDAO
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.expense_item_dao import ExpenseItemDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from dao.expense_receipt_dao import ExpenseReceiptDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from dao.expense_category_dao import ExpenseCategoryDAO
from utils import role_required

finance_controller = Blueprint("finance_controller", __name__, url_prefix="/finance")

claim_dao = ExpenseClaimDAO()
history_dao = ApprovalHistoryDAO()
reimbursement_dao = ReimbursementDAO()

finance_service = FinanceService(reimbursement_dao, claim_dao, history_dao)
expense_service = ExpenseService(
    claim_dao, ExpenseItemDAO(),
    ExpensePolicyDAO(), ExpenseReceiptDAO(), history_dao
)
category_dao = ExpenseCategoryDAO()

@finance_controller.route("/dashboard")
@role_required("finance_admin")
def dashboard():
    approved_claims = expense_service.get_by_status("approved")
    recent_reimbursements = finance_service.get_all_reimbursements()[:10]
    return render_template(
        "finance/dashboard.html",
        approved_claims=approved_claims,
        recent_reimbursements=recent_reimbursements
    )

@finance_controller.route("/process/<int:claim_id>", methods=["GET", "POST"])
@role_required("finance_admin")
def process_claim(claim_id):
    try:
        claim = expense_service.get_by_id(claim_id)
    except ValueError:
        return redirect("/finance/dashboard")
        
    if claim.status != "approved":
        return redirect("/finance/dashboard")

    if request.method == "GET":
        history = expense_service.get_history(claim_id)
        categories = category_dao.get_all()
        return render_template("finance/process_reimbursement.html", claim=claim, history=history, categories=categories)

    # POST processing
    payment_method = request.form.get("payment_method")
    transaction_reference = request.form.get("transaction_reference")
    notes = request.form.get("notes")

    try:
        finance_service.process_reimbursement(
            claim_id=claim_id,
            finance_user_id=session.get("user_id"),
            payment_method=payment_method,
            transaction_reference=transaction_reference,
            notes=notes
        )
    except ValueError as e:
        history = expense_service.get_history(claim_id)
        categories = category_dao.get_all()
        return render_template("finance/process_reimbursement.html", claim=claim, history=history, categories=categories, error=str(e))

    return redirect("/finance/dashboard")
