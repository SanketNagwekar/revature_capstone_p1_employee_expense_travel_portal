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
    receipts = db.relationship("ExpenseReceipt", back_populates="item", cascade="all, delete-orphan")

    def __init__(self, claim_id=None, category_id=None, description=None, amount=None, expense_date=None, **kwargs):
        super().__init__(**kwargs)
        if claim_id is not None:
            self.claim_id = claim_id
        if category_id is not None:
            self.category_id = category_id
        if description is not None:
            self.description = description
        if amount is not None:
            self.amount = amount
        if expense_date is not None:
            self.expense_date = expense_date

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
