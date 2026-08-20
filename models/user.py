from config.database import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # employee, manager, finance_admin, system_admin
    is_active = db.Column(db.Boolean, default=True)

    employee = db.relationship("Employee", back_populates="user", uselist=False)

    def __init__(self, username, password_hash, role, is_active=True):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active
        }
