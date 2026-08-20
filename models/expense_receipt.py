from config.database import db
from datetime import datetime

class ExpenseReceipt(db.Model):
    __tablename__ = "expense_receipts"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("expense_items.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    item = db.relationship("ExpenseItem", back_populates="receipts")

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "uploaded_at": str(self.uploaded_at)
        }
