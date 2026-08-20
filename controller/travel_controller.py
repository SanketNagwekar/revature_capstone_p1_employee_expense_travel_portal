from flask import Blueprint, request, render_template, redirect, session
from service.travel_service import TravelService
from dao.travel_request_dao import TravelRequestDAO
from utils import role_required
from datetime import date, datetime

travel_controller = Blueprint("travel_controller", __name__, url_prefix="/travel")

travel_service = TravelService(TravelRequestDAO())

@travel_controller.route("/new", methods=["GET", "POST"])
@role_required("employee")
def new_request():
    if request.method == "GET":
        return render_template("employee/travel_request.html")

    try:
        travel_date = datetime.strptime(request.form.get("travel_date"), "%Y-%m-%d").date()
        return_date = datetime.strptime(request.form.get("return_date"), "%Y-%m-%d").date()
        estimated_cost_raw = request.form.get("estimated_cost")
        estimated_cost = float(estimated_cost_raw) if estimated_cost_raw else None

        travel_service.create_request(
            employee_id=session.get("employee_id"),
            destination=request.form.get("destination"),
            purpose=request.form.get("purpose"),
            travel_date=travel_date,
            return_date=return_date,
            estimated_cost=estimated_cost
        )
        return redirect("/employee/dashboard")
    except ValueError as e:
        return render_template("employee/travel_request.html", error=str(e))

@travel_controller.route("/my")
@role_required("employee")
def my_requests():
    requests_list = travel_service.get_by_employee(session.get("employee_id"))
    return render_template("employee/my_travel.html", travel_requests=requests_list)
