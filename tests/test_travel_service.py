import pytest
import app
from datetime import date
from unittest.mock import MagicMock
from service.travel_service import TravelService
from models.travel_request import TravelRequest

@pytest.fixture
def travel_dao_mock():
    return MagicMock()

@pytest.fixture
def travel_service(travel_dao_mock):
    return TravelService(travel_dao_mock)

def test_create_request_success(travel_service, travel_dao_mock):
    travel_dao_mock.save.return_value = TravelRequest(id=1, status="pending")
    
    tr = travel_service.create_request(
        employee_id=1,
        destination="Delhi",
        purpose="Client Meeting",
        travel_date=date(2030, 1, 1),
        return_date=date(2030, 1, 5),
        estimated_cost=15000.0
    )
    
    assert tr.id == 1
    assert tr.status == "pending"
    travel_dao_mock.save.assert_called_once()

def test_create_request_past_date_fails(travel_service):
    with pytest.raises(ValueError, match="Travel date must be today or in the future"):
        travel_service.create_request(
            employee_id=1,
            destination="Delhi",
            purpose="Client Meeting",
            travel_date=date(2000, 1, 1),
            return_date=date(2030, 1, 5),
            estimated_cost=15000.0
        )

def test_create_request_return_before_travel_fails(travel_service):
    with pytest.raises(ValueError, match="Return date must be on or after the travel date"):
        travel_service.create_request(
            employee_id=1,
            destination="Delhi",
            purpose="Client Meeting",
            travel_date=date(2030, 1, 5),
            return_date=date(2030, 1, 1),
            estimated_cost=15000.0
        )

def test_approve_pending_request(travel_service, travel_dao_mock):
    mock_tr = TravelRequest(id=1, status="pending")
    travel_dao_mock.get_by_id.return_value = mock_tr
    travel_dao_mock.save.return_value = mock_tr
    
    tr = travel_service.approve(1)
    
    assert tr.status == "approved"
    travel_dao_mock.save.assert_called_once_with(mock_tr)

def test_approve_already_approved_fails(travel_service, travel_dao_mock):
    mock_tr = TravelRequest(id=1, status="approved")
    travel_dao_mock.get_by_id.return_value = mock_tr
    
    with pytest.raises(ValueError, match="Only pending requests can be approved"):
        travel_service.approve(1)
