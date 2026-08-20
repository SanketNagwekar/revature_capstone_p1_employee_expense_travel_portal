from config.database import db
from datetime import datetime

class ApprovalHistory(db.Model):
    __tablename__ = "approval_history"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("expense_claims.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # approved, rejected
    comments = db.Column(db.String(500))
    action_date = db.Column(db.DateTime, default=datetime.utcnow)

    claim = db.relationship("ExpenseClaim", back_populates="approval_history")
    reviewer = db.relationship("User")

    def __init__(self, claim_id, reviewer_id, action, comments=None):
        self.claim_id = claim_id
        self.reviewer_id = reviewer_id
        self.action = action
        self.comments = comments

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "reviewer_id": self.reviewer_id,
            "reviewer": self.reviewer.username if self.reviewer else None,
            "action": self.action,
            "comments": self.comments,
            "action_date": str(self.action_date)
        }
