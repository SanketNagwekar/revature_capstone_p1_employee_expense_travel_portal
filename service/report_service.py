from models.expense_claim import ExpenseClaim
from models.expense_item import ExpenseItem
from models.expense_category import ExpenseCategory
from models.employee import Employee
from sqlalchemy import func
from config.database import db

class ReportService:
    
    def get_expenses_by_category(self):
        # Returns list of (category_name, total_amount)
        results = db.session.query(
            ExpenseCategory.name,
            func.sum(ExpenseItem.amount).label("total")
        ).join(ExpenseItem, ExpenseItem.category_id == ExpenseCategory.id) \
         .group_by(ExpenseCategory.name).all()
         
        return [{"category": r.name, "total": float(r.total) if r.total else 0.0} for r in results]
        
    def get_expenses_by_department(self):
        # Returns list of (department, total_amount)
        # ExpenseClaim -> Employee
        results = db.session.query(
            Employee.department,
            func.sum(ExpenseClaim.total_amount).label("total")
        ).join(ExpenseClaim, ExpenseClaim.employee_id == Employee.id) \
         .filter(ExpenseClaim.status != "draft") \
         .group_by(Employee.department).all()
         
        return [{"department": r.department, "total": float(r.total) if r.total else 0.0} for r in results]
        
    def get_claims_by_status(self):
        # Returns list of (status, count)
        results = db.session.query(
            ExpenseClaim.status,
            func.count(ExpenseClaim.id).label("count")
        ).group_by(ExpenseClaim.status).all()
        
        return [{"status": r.status, "count": r.count} for r in results]
