from config.database import db

class ExpensePolicy(db.Model):
    __tablename__ = "expense_policies"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_categories.id"), nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

    category = db.relationship("ExpenseCategory", back_populates="policies")

    def __init__(self, category_id, max_amount, description=None):
        self.category_id = category_id
        self.max_amount = max_amount
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "max_amount": self.max_amount,
            "description": self.description
        }
