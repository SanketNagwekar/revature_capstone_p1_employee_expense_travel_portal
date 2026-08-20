from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User

class AuthService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def login(self, username, password):
        user = self.user_dao.get_by_username(username)
        if user is None:
            raise ValueError("Invalid username or password")
        if not user.is_active:
            raise ValueError("Account is inactive")
        if not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid username or password")
        return user

    def create_user(self, username, password, role):
        existing = self.user_dao.get_by_username(username)
        if existing:
            raise ValueError("Username already exists")
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        return self.user_dao.save(user)
