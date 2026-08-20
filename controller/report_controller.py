from flask import Blueprint, render_template
from service.report_service import ReportService
from utils import role_required

report_controller = Blueprint("report_controller", __name__, url_prefix="/admin/reports")
report_service = ReportService()

@report_controller.route("/")
@role_required("system_admin")
def reports_dashboard():
    cat_data = report_service.get_expenses_by_category()
    dept_data = report_service.get_expenses_by_department()
    status_data = report_service.get_claims_by_status()
    
    return render_template(
        "admin/reports.html",
        cat_data=cat_data,
        dept_data=dept_data,
        status_data=status_data
    )
