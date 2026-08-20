from models.reimbursement import Reimbursement
from models.approval_history import ApprovalHistory
from datetime import datetime

class FinanceService:
    def __init__(self, reimbursement_dao, claim_dao, history_dao):
        self.reimbursement_dao = reimbursement_dao
        self.claim_dao = claim_dao
        self.history_dao = history_dao

    def get_all_reimbursements(self):
        return self.reimbursement_dao.get_all()

    def process_reimbursement(self, claim_id, finance_user_id, payment_method, transaction_reference, notes):
        claim = self.claim_dao.get_by_id(claim_id)
        if claim is None:
            raise ValueError("Claim not found")
        
        if claim.status != "approved":
            raise ValueError("Only approved claims can be reimbursed")
        
        if self.reimbursement_dao.get_by_claim(claim_id):
            raise ValueError("Claim has already been reimbursed")

        reimbursement = Reimbursement(
            claim_id=claim_id,
            amount=claim.total_amount,
            payment_method=payment_method,
            transaction_reference=transaction_reference,
            notes=notes,
            processed_by=finance_user_id
        )
        self.reimbursement_dao.save(reimbursement)

        claim.status = "reimbursed"
        self.claim_dao.save(claim)

        history = ApprovalHistory(
            claim_id=claim_id,
            reviewer_id=finance_user_id,
            action="reimbursed",
            comments=notes
        )
        self.history_dao.save(history)

        return reimbursement
