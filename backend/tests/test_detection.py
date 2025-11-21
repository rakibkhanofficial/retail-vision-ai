import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Get authentication headers"""
    test_user = {
        "email": "analysis_test@example.com",
        "username": "analysistest",
        "full_name": "Analysis Test",
        "password": "testpass123"
    }
    
    client.post("/api/v1/auth/register", json=test_user)
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_ask_question_without_auth():
    """Test asking question without authentication"""
    response = client.post("/api/v1/analysis/ask", json={
        "detection_id": 1,
        "question": "What products do you see?"
    })
    assert response.status_code == 401

def test_ask_question_invalid_detection(auth_headers):
    """Test asking question about non-existent detection"""
    response = client.post("/api/v1/analysis/ask", json={
        "detection_id": 9999,
        "question": "What products do you see?"
    }, headers=auth_headers)
    assert response.status_code == 404

def test_ask_question_service_unavailable(auth_headers):
    """Test asking question when Gemini service is not available"""
    # This test assumes Gemini is not configured in test environment
    response = client.post("/api/v1/analysis/ask", json={
        "detection_id": 1,
        "question": "What products do you see?"
    }, headers=auth_headers)
    
    # Should either return service unavailable or not found
    assert response.status_code in [503, 404]

def test_get_statistics(auth_headers):
    """Test getting user statistics"""
    response = client.get("/api/v1/analysis/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_detections" in data
    assert "total_objects_detected" in data
    assert "average_objects_per_detection" in data
    assert "class_distribution" in data
    assert "most_detected_class" in data

def test_statistics_with_no_detections(auth_headers):
    """Test statistics for user with no detections"""
    response = client.get("/api/v1/analysis/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_detections"] >= 0
    assert data["total_objects_detected"] >= 0