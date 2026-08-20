from config.database import db
from datetime import datetime

class TravelRequest(db.Model):
    __tablename__ = "travel_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.String(500), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    estimated_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default="pending")  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="travel_requests")
    expense_claims = db.relationship("ExpenseClaim", back_populates="travel_request")

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "destination": self.destination,
            "purpose": self.purpose,
            "travel_date": str(self.travel_date),
            "return_date": str(self.return_date),
            "estimated_cost": self.estimated_cost,
            "status": self.status,
            "created_at": str(self.created_at)
        }
