from models.employee import Employee
from config.database import db

class EmployeeDAO:

    def get_all(self):
        return Employee.query.all()

    def get_by_id(self, emp_id):
        return Employee.query.get(emp_id)

    def get_by_user_id(self, user_id):
        return Employee.query.filter_by(user_id=user_id).first()

    def save(self, employee):
        db.session.add(employee)
        db.session.commit()
        return employee

    def delete(self, employee):
        db.session.delete(employee)
        db.session.commit()
