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


@pytest.mark.parametrize("time", ["13:30", "01:30 PM", "01:30 pm", 13 * 60 * 60 + 30 * 60])
def test_submit_appointment(test_client: TestClient, time) -> None:
    response = test_client.post(
        "/appointments",
        json={
            "id": 1,
            "serviceId": "2.02",
            "date": "2025-01-10",
            "time": time,
            "clientName": "Jane Doe",
            "clientPhone": "555-123-4567",
            "clientEmail": "janedoe@gmail.com",
            "payment": {
                "token": "token",
                "idempotencyKey": "idempotencyKey",
            },
        },
    )
    assert response.status_code == 200, response.content
    result = response.json()
    if result.get("id"):
        result["id"] = 1
    assert result == {
        "clientEmail": "janedoe@gmail.com",
        "clientName": "Jane Doe",
        "clientPhone": "555-123-4567",
        "date": "2025-01-10",
        "remindedAt": 0,
        "id": 1,
        "serviceId": "2.02",
        "time": "13:30:00",
        "depositToken": "J2xeb9aj55wS755Tw59hmjRKK3ZZY",
    }


def test_submit_appointment_without_token_fails(test_client: TestClient) -> None:
    response = test_client.post(
        "/appointments",
        json={
            "id": 1,
            "serviceId": "2.02",
            "date": "2025-01-10",
            "time": "01:30 pm",
            "clientName": "Jane Doe",
            "clientPhone": "555-123-4567",
            "clientEmail": "janedoe@gmail.com",
            "payment": {
                "token": "",
                "idempotencyKey": "idempotencyKey",
            },
        },
    )
    assert response.status_code == 422
    result = response.json()
    assert result == {
        "error": "no token",
    }
