from flask import Blueprint, jsonify, request, session
from service.travel_service import TravelService
from service.expense_service import ExpenseService
from service.finance_service import FinanceService
from dao.travel_request_dao import TravelRequestDAO
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.expense_item_dao import ExpenseItemDAO
from dao.expense_policy_dao import ExpensePolicyDAO
from dao.expense_receipt_dao import ExpenseReceiptDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from dao.reimbursement_dao import ReimbursementDAO
from utils import role_required

api_controller = Blueprint("api_controller", __name__, url_prefix="/api")

travel_service = TravelService(TravelRequestDAO())
expense_service = ExpenseService(
    ExpenseClaimDAO(), ExpenseItemDAO(), ExpensePolicyDAO(),
    ExpenseReceiptDAO(), ApprovalHistoryDAO()
)
finance_service = FinanceService(ReimbursementDAO(), ExpenseClaimDAO(), ApprovalHistoryDAO())

def get_user_id():
    return session.get("user_id")

def get_employee_id():
    return session.get("employee_id")

def get_role():
    return session.get("role")

def require_auth():
    if not get_user_id():
        return jsonify({"error": "Unauthenticated"}), 401
    return None

# ── Travel Requests API ──
@api_controller.route("/travel-requests", methods=["GET"])
def get_travel_requests():
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() == "employee":
        trs = travel_service.get_by_employee(get_employee_id())
    elif get_role() in ["manager", "system_admin"]:
        trs = travel_service.get_all()
    else:
        return jsonify({"error": "Unauthorized"}), 403
        
    return jsonify([t.to_dict() for t in trs]), 200

@api_controller.route("/travel-requests", methods=["POST"])
def create_travel_request():
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() != "employee":
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json() or {}
    try:
        from datetime import datetime
        travel_date = datetime.strptime(data.get("travel_date"), "%Y-%m-%d").date() if data.get("travel_date") else None
        return_date = datetime.strptime(data.get("return_date"), "%Y-%m-%d").date() if data.get("return_date") else None
        
        tr = travel_service.create_request(
            employee_id=get_employee_id(),
            destination=data.get("destination"),
            purpose=data.get("purpose"),
            travel_date=travel_date,
            return_date=return_date,
            estimated_cost=data.get("estimated_cost")
        )
        return jsonify(tr.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_controller.route("/travel-requests/<int:tr_id>", methods=["GET"])
def get_travel_request(tr_id):
    auth_err = require_auth()
    if auth_err: return auth_err
    
    try:
        tr = travel_service.get_by_id(tr_id)
        if get_role() == "employee" and tr.employee_id != get_employee_id():
            return jsonify({"error": "Unauthorized"}), 403
        return jsonify(tr.to_dict()), 200
    except ValueError:
        return jsonify({"error": "Not found"}), 404

# ── Claims API ──
@api_controller.route("/claims", methods=["GET"])
def get_claims():
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() == "employee":
        claims = expense_service.get_by_employee(get_employee_id())
    elif get_role() == "manager":
        claims = expense_service.get_by_status("submitted")
    elif get_role() == "finance_admin":
        claims = expense_service.get_by_status("finance_verified")
    elif get_role() == "system_admin":
        claims = expense_service.get_all() # Just return all for admin
    else:
        return jsonify({"error": "Unauthorized"}), 403
        
    return jsonify([c.to_dict() for c in claims]), 200

@api_controller.route("/claims", methods=["POST"])
def create_claim():
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() != "employee":
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json() or {}
    
    tr_id = data.get("travel_request_id")
    if tr_id:
        try:
            tr = travel_service.get_by_id(tr_id)
            if tr.employee_id != get_employee_id():
                return jsonify({"error": "Travel request belongs to another employee"}), 403
            if tr.status != "approved":
                return jsonify({"error": "Travel request must be approved"}), 400
        except ValueError:
            return jsonify({"error": "Travel request not found"}), 404
            
    try:
        claim = expense_service.create_claim(
            employee_id=get_employee_id(),
            title=data.get("title"),
            description=data.get("description"),
            travel_request_id=data.get("travel_request_id")
        )
        return jsonify(claim.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_controller.route("/claims/<int:claim_id>", methods=["GET"])
def get_claim(claim_id):
    auth_err = require_auth()
    if auth_err: return auth_err
    
    try:
        claim = expense_service.get_by_id(claim_id)
        if get_role() == "employee" and claim.employee_id != get_employee_id():
            return jsonify({"error": "Unauthorized"}), 403
        return jsonify(claim.to_dict()), 200
    except ValueError:
        return jsonify({"error": "Not found"}), 404

# ── Reimbursements API ──
@api_controller.route("/reimbursements", methods=["GET"])
def get_reimbursements():
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() not in ["finance_admin", "system_admin"]:
        return jsonify({"error": "Unauthorized"}), 403
        
    reimbursements = finance_service.get_all_reimbursements()
    return jsonify([r.to_dict() for r in reimbursements]), 200

@api_controller.route("/claims/<int:claim_id>/verify", methods=["POST"])
def verify_claim(claim_id):
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() != "finance_admin":
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json() or {}
    comments = data.get("comments", "Verified via API")
    
    try:
        claim = finance_service.verify_claim(claim_id, get_user_id(), comments)
        return jsonify(claim.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_controller.route("/claims/<int:claim_id>/reimburse", methods=["POST"])
def reimburse_claim(claim_id):
    auth_err = require_auth()
    if auth_err: return auth_err
    
    if get_role() != "finance_admin":
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json() or {}
    payment_method = data.get("payment_method", "Direct Deposit")
    transaction_reference = data.get("transaction_reference", "TX-API")
    notes = data.get("notes", "Processed via API")
    
    try:
        reimbursement = finance_service.process_reimbursement(
            claim_id, get_user_id(), payment_method, transaction_reference, notes
        )
        return jsonify(reimbursement.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
