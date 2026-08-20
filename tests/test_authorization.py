import pytest

def login(client, username, password="pass"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

def test_employee_cannot_access_manager_functionality(test_client):
    login(test_client, "emp1")
    response = test_client.get("/manager/dashboard")
    assert response.status_code == 302
    assert "/employee/dashboard" in response.headers["Location"] or "/login" in response.headers["Location"]

def test_employee_cannot_access_finance_functionality(test_client):
    login(test_client, "emp1")
    response = test_client.get("/finance/dashboard")
    assert response.status_code == 302

def test_employee_cannot_access_another_employee_claim(test_client):
    login(test_client, "emp2")
    response = test_client.get("/expense/1")
    # Should redirect away because claim 1 belongs to emp1
    assert response.status_code == 302
    assert "/employee/dashboard" in response.headers["Location"]

def test_employee_cannot_access_another_employee_receipt(test_client):
    login(test_client, "emp2")
    response = test_client.get("/expense/receipt/1/download")
    assert response.status_code == 302
    assert "/employee/dashboard" in response.headers["Location"]

def test_manager_can_access_receipt(test_client, monkeypatch):
    # Mock send_from_directory so it doesn't crash on fake file path
    monkeypatch.setattr("controller.expense_controller.send_from_directory", lambda *args, **kwargs: "file_content")
    
    login(test_client, "manager")
    response = test_client.get("/expense/receipt/1/download")
    assert response.status_code == 200
    assert response.data == b"file_content"

def test_finance_can_access_receipt(test_client, monkeypatch):
    monkeypatch.setattr("controller.expense_controller.send_from_directory", lambda *args, **kwargs: "file_content")
    
    login(test_client, "finance")
    response = test_client.get("/expense/receipt/1/download")
    assert response.status_code == 200
    assert response.data == b"file_content"
