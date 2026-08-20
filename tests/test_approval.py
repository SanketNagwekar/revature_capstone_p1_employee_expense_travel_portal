import pytest
from service.expense_service import ExpenseService
from dao.expense_claim_dao import ExpenseClaimDAO
from dao.approval_history_dao import ApprovalHistoryDAO
from models.expense_claim import ExpenseClaim
from unittest.mock import Mock

@pytest.fixture
def approval_service():
    claim_dao = Mock(spec=ExpenseClaimDAO)
    history_dao = Mock(spec=ApprovalHistoryDAO)
    
    # We only care about approval logic, which uses claim_dao and history_dao
    service = ExpenseService(claim_dao, Mock(), Mock(), Mock(), history_dao)
    return service, claim_dao, history_dao

def test_manager_approves_submitted_claim(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "submitted"
    claim_dao.get_by_id.return_value = claim
    
    result = service.approve_claim(1, 2, "Looks good")
    
    assert result.status == "approved"
    claim_dao.save.assert_called_once_with(claim)
    history_dao.save.assert_called_once()
    
def test_manager_rejects_submitted_claim(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "submitted"
    claim_dao.get_by_id.return_value = claim
    
    result = service.reject_claim(1, 2, "Too expensive")
    
    assert result.status == "rejected"
    claim_dao.save.assert_called_once_with(claim)
    history_dao.save.assert_called_once()

def test_invalid_claim_state_cannot_be_approved(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "draft"  # Cannot approve draft
    claim_dao.get_by_id.return_value = claim
    
    with pytest.raises(ValueError, match="Only submitted claims"):
        service.approve_claim(1, 2, "OK")

def test_invalid_claim_state_cannot_be_rejected(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "reimbursed"  # Cannot reject reimbursed
    claim_dao.get_by_id.return_value = claim
    
    with pytest.raises(ValueError, match="Only submitted claims"):
        service.reject_claim(1, 2, "No")

def test_rejection_comments_are_validated(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "submitted"
    claim_dao.get_by_id.return_value = claim
    
    with pytest.raises(ValueError, match="Comments are required"):
        service.reject_claim(1, 2, "")

def test_approval_history_is_created(approval_service):
    service, claim_dao, history_dao = approval_service
    claim = ExpenseClaim()
    claim.id = 1
    claim.status = "submitted"
    claim_dao.get_by_id.return_value = claim
    
    service.approve_claim(1, 2, "Approved by manager")
    
    history_dao.save.assert_called_once()
    history_obj = history_dao.save.call_args[0][0]
    assert history_obj.claim_id == 1
    assert history_obj.reviewer_id == 2
    assert history_obj.action == "approved"
    assert history_obj.comments == "Approved by manager"
