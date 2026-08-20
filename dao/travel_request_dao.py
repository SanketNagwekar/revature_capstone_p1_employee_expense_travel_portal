from models.travel_request import TravelRequest
from config.database import db

class TravelRequestDAO:

    def get_all(self):
        return TravelRequest.query.order_by(TravelRequest.created_at.desc()).all()

    def get_by_id(self, request_id):
        return TravelRequest.query.get(request_id)

    def get_by_employee(self, employee_id):
        return TravelRequest.query.filter_by(employee_id=employee_id).order_by(TravelRequest.created_at.desc()).all()

    def get_pending(self):
        return TravelRequest.query.filter_by(status="pending").order_by(TravelRequest.created_at.desc()).all()

    def save(self, travel_request):
        db.session.add(travel_request)
        db.session.commit()
        return travel_request
