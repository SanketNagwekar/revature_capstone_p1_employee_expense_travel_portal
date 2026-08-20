from models.employee import Employee

class EmployeeService:
    def __init__(self, employee_dao):
        self.employee_dao = employee_dao

    def get_by_id(self, emp_id):
        emp = self.employee_dao.get_by_id(emp_id)
        if emp is None:
            raise ValueError("Employee not found")
        return emp

    def get_by_user_id(self, user_id):
        emp = self.employee_dao.get_by_user_id(user_id)
        if emp is None:
            raise ValueError("Employee profile not found")
        return emp

    def update_profile(self, emp_id, full_name, department, designation, phone):
        emp = self.get_by_id(emp_id)
        emp.full_name = full_name
        emp.department = department
        emp.designation = designation
        emp.phone = phone
        return self.employee_dao.save(emp)
