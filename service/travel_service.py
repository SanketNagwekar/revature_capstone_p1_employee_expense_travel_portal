from datetime import date
from models.travel_request import TravelRequest

class TravelService:
    def __init__(self, travel_dao):
        self.travel_dao = travel_dao

    def get_all(self):
        return self.travel_dao.get_all()

    def get_by_employee(self, employee_id):
        return self.travel_dao.get_by_employee(employee_id)

    def get_pending(self):
        return self.travel_dao.get_pending()

    def get_by_id(self, request_id):
        tr = self.travel_dao.get_by_id(request_id)
        if tr is None:
            raise ValueError("Travel request not found")
        return tr

    def create_request(self, employee_id, destination, purpose, travel_date, return_date, estimated_cost):
        if not destination or not purpose:
            raise ValueError("Destination and purpose are required")
        if travel_date < date.today():
            raise ValueError("Travel date must be today or in the future")
        if return_date < travel_date:
            raise ValueError("Return date must be on or after the travel date")
        if estimated_cost is not None and estimated_cost < 0:
            raise ValueError("Estimated cost cannot be negative")

        tr = TravelRequest(
            employee_id=employee_id,
            destination=destination,
            purpose=purpose,
            travel_date=travel_date,
            return_date=return_date,
            estimated_cost=estimated_cost,
            status="pending"
        )
        return self.travel_dao.save(tr)

    def approve(self, request_id):
        tr = self.get_by_id(request_id)
        if tr.status != "pending":
            raise ValueError("Only pending requests can be approved")
        tr.status = "approved"
        return self.travel_dao.save(tr)

    def reject(self, request_id):
        tr = self.get_by_id(request_id)
        if tr.status != "pending":
            raise ValueError("Only pending requests can be rejected")
        tr.status = "rejected"
        return self.travel_dao.save(tr)
