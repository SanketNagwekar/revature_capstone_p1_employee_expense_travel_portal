from models.expense_category import ExpenseCategory
from config.database import db

class ExpenseCategoryDAO:

    def get_all(self):
        return ExpenseCategory.query.all()

    def get_by_id(self, cat_id):
        return ExpenseCategory.query.get(cat_id)

    def get_by_name(self, name):
        return ExpenseCategory.query.filter_by(name=name).first()

    def save(self, category):
        db.session.add(category)
        db.session.commit()
        return category

    def delete(self, category):
        db.session.delete(category)
        db.session.commit()
