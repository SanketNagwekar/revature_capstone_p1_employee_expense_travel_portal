from models.reimbursement import Reimbursement
from config.database import db

class ReimbursementDAO:

    def get_all(self):
        return Reimbursement.query.order_by(Reimbursement.processed_at.desc()).all()

    def get_by_claim(self, claim_id):
        return Reimbursement.query.filter_by(claim_id=claim_id).first()

    def save(self, reimbursement):
        db.session.add(reimbursement)
        db.session.commit()
        return reimbursement
