from models.expense_claim import ExpenseClaim
from config.database import db

class ExpenseClaimDAO:

    def get_all(self):
        return ExpenseClaim.query.order_by(ExpenseClaim.created_at.desc()).all()

    def get_by_id(self, claim_id):
        return ExpenseClaim.query.get(claim_id)

    def get_by_employee(self, employee_id, search_term=None):
        query = ExpenseClaim.query.filter_by(employee_id=employee_id)
        if search_term:
            from sqlalchemy import or_
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    ExpenseClaim.title.ilike(search_pattern),
                    ExpenseClaim.description.ilike(search_pattern),
                    db.cast(ExpenseClaim.id, db.String).ilike(search_pattern)
                )
            )
        return query.order_by(ExpenseClaim.created_at.desc()).all()

    def get_by_status(self, status):
        return ExpenseClaim.query.filter_by(status=status).order_by(ExpenseClaim.created_at.desc()).all()

    def save(self, claim):
        db.session.add(claim)
        db.session.commit()
        return claim
