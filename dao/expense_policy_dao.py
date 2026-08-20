from models.expense_policy import ExpensePolicy
from config.database import db

class ExpensePolicyDAO:

    def get_all(self):
        return ExpensePolicy.query.all()

    def get_by_id(self, policy_id):
        return ExpensePolicy.query.get(policy_id)

    def get_by_category(self, category_id):
        return ExpensePolicy.query.filter_by(category_id=category_id).first()

    def save(self, policy):
        db.session.add(policy)
        db.session.commit()
        return policy

    def delete(self, policy):
        db.session.delete(policy)
        db.session.commit()
