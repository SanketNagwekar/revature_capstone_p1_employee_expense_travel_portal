from config.database import db

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    user = db.relationship("User", back_populates="employee")
    travel_requests = db.relationship("TravelRequest", back_populates="employee", cascade="all, delete-orphan")
    expense_claims = db.relationship("ExpenseClaim", back_populates="employee", cascade="all, delete-orphan")

    def __init__(self, user_id, full_name, department=None, designation=None, phone=None):
        self.user_id = user_id
        self.full_name = full_name
        self.department = department
        self.designation = designation
        self.phone = phone


    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "department": self.department,
            "designation": self.designation,
            "phone": self.phone
        }
