from datetime import datetime
from models.expense_claim import ExpenseClaim
from models.expense_item import ExpenseItem
from models.expense_receipt import ExpenseReceipt
from models.approval_history import ApprovalHistory

class ExpenseService:
    def __init__(self, claim_dao, item_dao, policy_dao, receipt_dao, history_dao):
        self.claim_dao = claim_dao
        self.item_dao = item_dao
        self.policy_dao = policy_dao
        self.receipt_dao = receipt_dao
        self.history_dao = history_dao

    def get_by_employee(self, employee_id):
        return self.claim_dao.get_by_employee(employee_id)

    def get_all(self):
        return self.claim_dao.get_all()

    def get_by_status(self, status):
        return self.claim_dao.get_by_status(status)

    def get_by_id(self, claim_id):
        claim = self.claim_dao.get_by_id(claim_id)
        if claim is None:
            raise ValueError("Expense claim not found")
        return claim

    def create_claim(self, employee_id, title, description, travel_request_id=None):
        if not title:
            raise ValueError("Claim title is required")
        claim = ExpenseClaim(
            employee_id=employee_id,
            travel_request_id=travel_request_id if travel_request_id else None,
            title=title,
            description=description,
            status="draft"
        )
        return self.claim_dao.save(claim)

    def add_item(self, claim_id, category_id, description, amount, expense_date):
        claim = self.get_by_id(claim_id)
        if claim.status not in ("draft",):
            raise ValueError("Items can only be added to draft claims")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        policy = self.policy_dao.get_by_category(category_id)
        if policy and amount > policy.max_amount:
            raise ValueError(f"Amount exceeds policy limit of {policy.max_amount} for this category")

        item = ExpenseItem(
            claim_id=claim_id,
            category_id=category_id,
            description=description,
            amount=amount,
            expense_date=expense_date
        )
        saved_item = self.item_dao.save(item)

        claim.total_amount = sum(i.amount for i in claim.expense_items)
        self.claim_dao.save(claim)
        return saved_item

    def delete_item(self, item_id):
        item = self.item_dao.get_by_id(item_id)
        if item is None:
            raise ValueError("Item not found")
        claim = self.claim_dao.get_by_id(item.claim_id)
        self.item_dao.delete(item)
        claim.total_amount = sum(i.amount for i in claim.expense_items)
        self.claim_dao.save(claim)

    def submit_claim(self, claim_id, employee_id):
        claim = self.get_by_id(claim_id)
        if claim.employee_id != employee_id:
            raise ValueError("Unauthorized")
        if claim.status != "draft":
            raise ValueError("Only draft claims can be submitted")
        if not claim.expense_items:
            raise ValueError("Cannot submit a claim with no items")
        claim.status = "submitted"
        claim.submitted_at = datetime.utcnow()
        return self.claim_dao.save(claim)

    def approve_claim(self, claim_id, reviewer_id, comments):
        claim = self.get_by_id(claim_id)
        if claim.status != "submitted":
            raise ValueError("Only submitted claims can be approved")
        claim.status = "approved"
        self.claim_dao.save(claim)
        history = ApprovalHistory(
            claim_id=claim_id,
            reviewer_id=reviewer_id,
            action="approved",
            comments=comments
        )
        self.history_dao.save(history)
        return claim

    def reject_claim(self, claim_id, reviewer_id, comments):
        claim = self.get_by_id(claim_id)
        if claim.status != "submitted":
            raise ValueError("Only submitted claims can be rejected")
        claim.status = "rejected"
        self.claim_dao.save(claim)
        history = ApprovalHistory(
            claim_id=claim_id,
            reviewer_id=reviewer_id,
            action="rejected",
            comments=comments
        )
        self.history_dao.save(history)
        return claim

    def get_history(self, claim_id):
        return self.history_dao.get_by_claim(claim_id)

    def upload_receipt(self, item_id, filename, file_path):
        item = self.item_dao.get_by_id(item_id)
        if item is None:
            raise ValueError("Expense item not found")
        receipt = ExpenseReceipt(item_id=item_id, filename=filename, file_path=file_path)
        return self.receipt_dao.save(receipt)

    def get_receipts_for_item(self, item_id):
        return self.receipt_dao.get_by_item(item_id)

    def get_receipt_by_id(self, receipt_id):
        receipt = self.receipt_dao.get_by_id(receipt_id)
        if receipt is None:
            raise ValueError("Receipt not found")
        return receipt

    def delete_receipt(self, receipt_id):
        receipt = self.receipt_dao.get_by_id(receipt_id)
        if receipt is None:
            raise ValueError("Receipt not found")
        import os
        if os.path.exists(receipt.file_path):
            os.remove(receipt.file_path)
        self.receipt_dao.delete(receipt)
