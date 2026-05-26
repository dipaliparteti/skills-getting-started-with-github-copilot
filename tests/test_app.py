"""
Tests for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src import app as app_module


@pytest.fixture
def client():
    """Fixture that provides a test client for the FastAPI app with fresh state"""
    # Reset activities to initial state before each test
    app_module.activities.clear()
    app_module.activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Outdoor team sport practice and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "maria@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Team training sessions and friendly games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["jake@mergington.edu", "lisa@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and creative projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["nina@mergington.edu", "leah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting skills and create theatrical performances",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu", "zoe@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["maya@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["sara@mergington.edu", "liam@mergington.edu"]
        }
    })
    
    return TestClient(app_module.app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is a dictionary with expected activities
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
    def test_get_activities_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_verifies_activity_added(self, client):
        """Test that student is actually added to participants"""
        email = "verifytest@mergington.edu"
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify by checking activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Drama Club"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup for same activity returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_same_student_different_activities(self, client):
        """Test that same student can sign up for multiple different activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Art Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_verifies_removal(self, client):
        """Test that student is actually removed from participants"""
        email = "michael@mergington.edu"
        
        # Verify they're in the list first
        activities_before = client.get("/activities").json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify they're removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after["Chess Club"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self, client):
        """Test unregistering non-enrolled student returns 404"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that student can re-signup after unregistering"""
        email = "rejoinstudent@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Science Olympiad/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Science Olympiad/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            "/activities/Science Olympiad/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email in activities["Science Olympiad"]["participants"]
