from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.config import Settings


@pytest.fixture(name="test_settings", scope="session")
def settings_fixture() -> Settings:
    return Settings.test_settings()


@pytest.fixture(name="test_client")
def client_fixture(test_settings: Settings) -> Iterator[TestClient]:
    assert not test_settings.enable_emails
    with TestClient(create_app(test_settings)) as client:
        yield client


def test_submit_appointment(test_client: TestClient) -> None:
    response = test_client.post(
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
