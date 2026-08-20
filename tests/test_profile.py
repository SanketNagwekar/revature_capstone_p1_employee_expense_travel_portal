import pytest
from unittest.mock import MagicMock
from service.employee_service import EmployeeService
from models.employee import Employee

@pytest.fixture
def employee_dao_mock():
    return MagicMock()

@pytest.fixture
def employee_service(employee_dao_mock):
    return EmployeeService(employee_dao_mock)

def test_update_profile(employee_service, employee_dao_mock):
    mock_emp = Employee(id=1, full_name="Old Name", department="Old Dept", designation="Old Desig", phone="123")
    employee_dao_mock.get_by_id.return_value = mock_emp
    employee_dao_mock.save.return_value = mock_emp
    
    updated_emp = employee_service.update_profile(
        emp_id=1,
        full_name="New Name",
        department="New Dept",
        designation="New Desig",
        phone="999"
    )
    
    assert updated_emp.full_name == "New Name"
    assert updated_emp.department == "New Dept"
    assert updated_emp.designation == "New Desig"
    assert updated_emp.phone == "999"
    employee_dao_mock.save.assert_called_once_with(mock_emp)
