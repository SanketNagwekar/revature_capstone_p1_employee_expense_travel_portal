import pytest
from unittest.mock import MagicMock
from datetime import datetime
from service.finance_service import FinanceService
from models.expense_claim import ExpenseClaim
from models.reimbursement import Reimbursement

@pytest.fixture
def reimbursement_dao_mock():
    return MagicMock()

@pytest.fixture
def claim_dao_mock():
    return MagicMock()

@pytest.fixture
def history_dao_mock():
    return MagicMock()

@pytest.fixture
def finance_service(reimbursement_dao_mock, claim_dao_mock, history_dao_mock):
    return FinanceService(reimbursement_dao_mock, claim_dao_mock, history_dao_mock)

def test_reimbursement_succeeds(finance_service, reimbursement_dao_mock, claim_dao_mock, history_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="finance_verified", total_amount=500.0)  # type: ignore          
    claim_dao_mock.get_by_id.return_value = mock_claim
    reimbursement_dao_mock.get_by_claim.return_value = None
    
    reimbursement = finance_service.process_reimbursement(
        claim_id=1,
        finance_user_id=10,
        payment_method="Bank Transfer",
        transaction_reference="TXN123",
        notes="Processed quickly"
    )
    
    assert reimbursement.claim_id == 1
    assert reimbursement.amount == 500.0
    assert reimbursement.payment_method == "Bank Transfer"
    assert reimbursement.transaction_reference == "TXN123"
    assert reimbursement.processed_by == 10
    
    assert mock_claim.status == "reimbursed"
    
    reimbursement_dao_mock.save.assert_called_once()
    claim_dao_mock.save.assert_called_once_with(mock_claim)
    history_dao_mock.save.assert_called_once()

def test_duplicate_reimbursement_rejected(finance_service, reimbursement_dao_mock, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="finance_verified", total_amount=500.0)  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    # Simulate already reimbursed
    reimbursement_dao_mock.get_by_claim.return_value = Reimbursement(id=1)  # type: ignore
    
    with pytest.raises(ValueError, match="Claim has already been reimbursed"):
        finance_service.process_reimbursement(
            claim_id=1,
            finance_user_id=10,
            payment_method="Bank Transfer",
            transaction_reference="TXN123",
            notes="Processed quickly"
        )

def test_unapproved_claim_rejected(finance_service, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="submitted", total_amount=500.0)  # type: ignore
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Only verified claims can be reimbursed"):
        finance_service.process_reimbursement(
            claim_id=1,
            finance_user_id=10,
            payment_method="Bank Transfer",
            transaction_reference="TXN123",
            notes="Processed quickly"
        )

def test_verify_claim(finance_service, claim_dao_mock, history_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="approved", total_amount=500.0)
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    finance_service.verify_claim(claim_id=1, finance_user_id=10, comments="Verified ok")
    
    assert mock_claim.status == "finance_verified"
    claim_dao_mock.save.assert_called_once_with(mock_claim)
    history_dao_mock.save.assert_called_once()

def test_verify_unapproved_claim_fails(finance_service, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="submitted", total_amount=500.0)
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Only approved claims can be finance-verified"):
        finance_service.verify_claim(claim_id=1, finance_user_id=10, comments="Failed verify")

def test_duplicate_verification_rejected(finance_service, claim_dao_mock):
    mock_claim = ExpenseClaim(id=1, status="finance_verified", total_amount=500.0)
    claim_dao_mock.get_by_id.return_value = mock_claim
    
    with pytest.raises(ValueError, match="Claim is already verified"):
        finance_service.verify_claim(claim_id=1, finance_user_id=10, comments="Duplicate verify")
