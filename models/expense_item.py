from config.database import db

class ExpenseItem(db.Model):
    __tablename__ = "expense_items"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("expense_claims.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_categories.id"), nullable=False)
    description = db.Column(db.String(300))
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, nullable=False)

    claim = db.relationship("ExpenseClaim", back_populates="expense_items")
    category = db.relationship("ExpenseCategory", back_populates="expense_items")
    receipts = db.relationship("ExpenseReceipt", back_populates="item")

    def to_dict(self):
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "description": self.description,
            "amount": self.amount,
            "expense_date": str(self.expense_date)
        }
