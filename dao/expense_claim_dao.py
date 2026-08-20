from models.expense_claim import ExpenseClaim
from config.database import db

class ExpenseClaimDAO:

    def get_all(self):
        return ExpenseClaim.query.order_by(ExpenseClaim.created_at.desc()).all()

    def get_by_id(self, claim_id):
        return ExpenseClaim.query.get(claim_id)

    def get_by_employee(self, employee_id):
        return ExpenseClaim.query.filter_by(employee_id=employee_id).order_by(ExpenseClaim.created_at.desc()).all()

    def get_by_status(self, status):
        return ExpenseClaim.query.filter_by(status=status).order_by(ExpenseClaim.created_at.desc()).all()

    def save(self, claim):
        db.session.add(claim)
        db.session.commit()
        return claim
