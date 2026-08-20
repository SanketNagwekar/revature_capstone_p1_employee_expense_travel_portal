from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from config.database import init_db, db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

init_db(app)

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
app.register_blueprint(auth_controller)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
