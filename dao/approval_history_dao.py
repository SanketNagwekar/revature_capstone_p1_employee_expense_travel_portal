from models.approval_history import ApprovalHistory
from config.database import db

class ApprovalHistoryDAO:

    def get_by_claim(self, claim_id):
        return ApprovalHistory.query.filter_by(claim_id=claim_id).order_by(ApprovalHistory.action_date.desc()).all()

    def save(self, history):
        db.session.add(history)
        db.session.commit()
        return history
