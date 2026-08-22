from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from config.database import init_db, db
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY") # Use same secret for JWT
jwt = JWTManager(app)

init_db(app)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

from models.user import User
from models.employee import Employee
from models.expense_category import ExpenseCategory
from models.expense_policy import ExpensePolicy
from models.travel_request import TravelRequest
from models.expense_claim import ExpenseClaim
from models.expense_item import ExpenseItem
from models.expense_receipt import ExpenseReceipt
from models.approval_history import ApprovalHistory
from models.reimbursement import Reimbursement

from controller.auth_controller import auth_controller
from controller.admin_controller import admin_controller
from controller.api_controller import api_controller
from controller.employee_controller import employee_controller
from controller.travel_controller import travel_controller
from controller.expense_controller import expense_controller
from controller.manager_controller import manager_controller
from controller.finance_controller import finance_controller
from controller.report_controller import report_controller
app.register_blueprint(auth_controller)
app.register_blueprint(admin_controller)
app.register_blueprint(api_controller)
app.register_blueprint(employee_controller)
app.register_blueprint(travel_controller)
app.register_blueprint(expense_controller)
app.register_blueprint(manager_controller)
app.register_blueprint(finance_controller)
app.register_blueprint(report_controller)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
