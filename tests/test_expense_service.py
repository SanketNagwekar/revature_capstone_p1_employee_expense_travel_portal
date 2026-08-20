import pytest
import app
from datetime import date
from unittest.mock import MagicMock
from service.expense_service import ExpenseService
from models.expense_claim import ExpenseClaim
from models.expense_policy import ExpensePolicy
from models.expense_item import ExpenseItem

@pytest.fixture
def claim_dao_mock():
    return MagicMock()

@pytest.fixture
def item_dao_mock():
    return MagicMock()

@pytest.fixture
def policy_dao_mock():
    return MagicMock()

@pytest.fixture
def receipt_dao_mock():
    return MagicMock()

@pytest.fixture
def history_dao_mock():
    return MagicMock()

@pytest.fixture
def expense_service(claim_dao_mock, item_dao_mock, policy_dao_mock, receipt_dao_mock, history_dao_mock):
    return ExpenseService(claim_dao_mock, item_dao_mock, policy_dao_mock, receipt_dao_mock, history_dao_mock)

def test_add_item_within_policy(expense_service, claim_dao_mock, item_dao_mock, policy_dao_mock):
    # Mock draft claim
    mock_claim = ExpenseClaim(id=1, status="draft", employee_id=5, expense_items=[])  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    # Mock policy
    mock_policy = ExpensePolicy(category_id=2, max_amount=100.0)  # type: ignore
    policy_dao_mock.get_by_category.return_value = mock_policy
    
    # Mock save item
    mock_item = ExpenseItem(id=1, claim_id=1, amount=50.0)  # type: ignore
    item_dao_mock.save.return_value = mock_item
    
    # Test
    item = expense_service.add_item(
        claim_id=1,
        category_id=2,
        description="Lunch",
        amount=50.0,
        expense_date=date(2026, 8, 20),
        employee_id=5
    )
    
    assert item.id == 1
    item_dao_mock.save.assert_called_once()
    claim_dao_mock.save.assert_called_once() # Updates total_amount

def test_add_item_exceeds_policy(expense_service, claim_dao_mock, policy_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="draft", employee_id=5, expense_items=[])  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    mock_policy = ExpensePolicy(category_id=2, max_amount=100.0)  # type: ignore
    policy_dao_mock.get_by_category.return_value = mock_policy
    
    with pytest.raises(ValueError, match="Amount exceeds policy limit of 100.0"):
        expense_service.add_item(
            claim_id=1,
            category_id=2,
            description="Fancy Dinner",
            amount=150.0,
            expense_date=date(2026, 8, 20),
            employee_id=5
        )

def test_add_item_unauthorized(expense_service, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="draft", employee_id=5, expense_items=[])  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Unauthorized"):
        expense_service.add_item(
            claim_id=1,
            category_id=2,
            description="Lunch",
            amount=50.0,
            expense_date=date(2026, 8, 20),
            employee_id=999 # Wrong employee
        )

def test_delete_item_unauthorized(expense_service, item_dao_mock, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, employee_id=5)  # type: ignore
    mock_item = ExpenseItem(id=1, claim_id=1)  # type: ignore
    item_dao_mock.get_by_id.return_value = mock_item
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Unauthorized"):
        expense_service.delete_item(1, employee_id=999)

def test_submit_empty_claim_fails(expense_service, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="draft", employee_id=5, expense_items=[])  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Cannot submit a claim with no items"):
        expense_service.submit_claim(claim_id=1, employee_id=5)

def test_submit_claim_success(expense_service, claim_dao_mock):
    mock_item = ExpenseItem(id=1, amount=50.0)  # type: ignore
    mock_claim = ExpenseClaim(id=1, status="draft", employee_id=5, expense_items=[mock_item])  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    claim_dao_mock.save.return_value = mock_claim
    
    expense_service.submit_claim(claim_id=1, employee_id=5)
    
    assert mock_claim.status == "submitted"
    assert mock_claim.submitted_at is not None
    claim_dao_mock.save.assert_called_once_with(mock_claim)
