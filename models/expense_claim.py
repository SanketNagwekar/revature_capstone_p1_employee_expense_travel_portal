from config.database import db
from datetime import datetime

class ExpenseClaim(db.Model):
    __tablename__ = "expense_claims"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    travel_request_id = db.Column(db.Integer, db.ForeignKey("travel_requests.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="draft")  # draft, submitted, approved, rejected, reimbursed
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="expense_claims")
    travel_request = db.relationship("TravelRequest", back_populates="expense_claims")
    expense_items = db.relationship("ExpenseItem", back_populates="claim")
    approval_history = db.relationship("ApprovalHistory", back_populates="claim")
    reimbursement = db.relationship("Reimbursement", back_populates="claim", uselist=False)

    def __init__(self, employee_id=None, travel_request_id=None, title=None, description=None, total_amount=0.0, status="draft", submitted_at=None, created_at=None, **kwargs):
        super().__init__(**kwargs)
        if employee_id is not None:
            self.employee_id = employee_id
        if travel_request_id is not None:
            self.travel_request_id = travel_request_id
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if total_amount is not None:
            self.total_amount = total_amount
        if status is not None:
            self.status = status
        if submitted_at is not None:
            self.submitted_at = submitted_at
        if created_at is not None:
            self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "travel_request_id": self.travel_request_id,
            "title": self.title,
            "description": self.description,
            "total_amount": self.total_amount,
            "status": self.status,
            "submitted_at": str(self.submitted_at) if self.submitted_at else None,
            "created_at": str(self.created_at)
        }
