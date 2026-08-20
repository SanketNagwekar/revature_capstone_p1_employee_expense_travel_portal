import pytest
from app import app
from controller.expense_controller import allowed_file

def test_allowed_file():
    assert allowed_file("receipt.pdf") is True
    assert allowed_file("photo.jpg") is True
    assert allowed_file("image.png") is True
    assert allowed_file("scanned.jpeg") is True
    assert allowed_file("animation.gif") is True
    
    assert allowed_file("script.sh") is False
    assert allowed_file("program.exe") is False
    assert allowed_file("document.docx") is False
    assert allowed_file("noextension") is False
    assert allowed_file(".hiddenfile") is False

def test_upload_oversized_file(test_client):
    # This requires using the client to post a large file and check for 413 or the app's handling.
    # Flask MAX_CONTENT_LENGTH will automatically reject large files with 413 before reaching the controller.
    # Since we configured MAX_CONTENT_LENGTH = 5 * 1024 * 1024 in app.py, let's test it.
    from tests.test_authorization import login
    import io
    
    login(test_client, "emp1")
    
    # Create a dummy file larger than 5MB
    large_file_content = b"0" * (6 * 1024 * 1024)
    data = {
        "receipt": (io.BytesIO(large_file_content), "large.pdf")
    }
    
    response = test_client.post("/expense/1/upload-receipt/1", data=data, content_type="multipart/form-data")
    assert response.status_code == 413 # Request Entity Too Large
