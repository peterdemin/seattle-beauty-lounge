from fastapi.testclient import TestClient

from api.main import app


def test_submit_appointment():
    client = TestClient(app)
    response = client.post(
        "/appointments",
        json={
            "id": 1,
            "serviceId": "haircut-123",
            "date": "2025-01-10",
            "time": "13:30",
            "clientName": "Jane Doe",
            "clientPhone": "555-123-4567",
            "clientEmail": "janedoe@gmail.com",
        },
    )
    assert response.status_code == 200
    result = response.json()
    result["id"] = 1
    assert result == {
        "clientEmail": "janedoe@gmail.com",
        "clientName": "Jane Doe",
        "clientPhone": "555-123-4567",
        "date": "2025-01-10",
        "id": 1,
        "serviceId": "haircut-123",
        "time": "13:30",
    }
