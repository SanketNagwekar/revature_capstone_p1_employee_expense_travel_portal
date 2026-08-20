from models.expense_item import ExpenseItem
from config.database import db

class ExpenseItemDAO:

    def get_by_claim(self, claim_id):
        return ExpenseItem.query.filter_by(claim_id=claim_id).all()

    def get_by_id(self, item_id):
        return ExpenseItem.query.get(item_id)

    def save(self, item):
        db.session.add(item)
        db.session.commit()
        return item

    def delete(self, item):
        db.session.delete(item)
        db.session.commit()
