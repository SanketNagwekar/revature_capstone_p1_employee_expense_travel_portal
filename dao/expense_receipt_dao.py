from models.expense_receipt import ExpenseReceipt
from config.database import db

class ExpenseReceiptDAO:

    def get_by_item(self, item_id):
        return ExpenseReceipt.query.filter_by(item_id=item_id).all()

    def get_by_id(self, receipt_id):
        return ExpenseReceipt.query.get(receipt_id)

    def save(self, receipt):
        db.session.add(receipt)
        db.session.commit()
        return receipt

    def delete(self, receipt):
        db.session.delete(receipt)
        db.session.commit()
