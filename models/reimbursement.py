from config.database import db
from datetime import datetime

class Reimbursement(db.Model):
    __tablename__ = "reimbursements"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("expense_claims.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    processed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="processed")  # processed

    claim = db.relationship("ExpenseClaim", back_populates="reimbursement")
    finance_user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "amount": self.amount,
            "processed_by": self.finance_user.username if self.finance_user else None,
            "processed_at": str(self.processed_at),
            "status": self.status
        }
