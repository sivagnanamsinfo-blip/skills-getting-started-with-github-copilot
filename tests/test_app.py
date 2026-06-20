import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def activity_path(activity_name: str) -> str:
    return quote(activity_name, safe="")


def signup_url(activity_name: str) -> str:
    return f"/activities/{activity_path(activity_name)}/signup"


def unregister_url(activity_name: str) -> str:
    return f"/activities/{activity_path(activity_name)}/participants"


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)
    assert data[expected_activity]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    url = signup_url("Chess Club")

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_email():
    # Arrange
    email = "michael@mergington.edu"
    url = signup_url("Chess Club")

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_existing_participant():
    # Arrange
    email = "michael@mergington.edu"
    url = unregister_url("Chess Club")

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]
