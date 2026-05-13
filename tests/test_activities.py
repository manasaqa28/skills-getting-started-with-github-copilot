"""Tests for activities endpoints using AAA (Arrange-Act-Assert) pattern"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully fetching all activities"""
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert expected_activity in activities

    def test_get_activities_structure(self, client):
        """Test that activities have correct structure"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, sample_email, sample_activity):
        """Test successfully signing up for an activity"""
        # Arrange
        activity_name = sample_activity
        email = sample_email
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_email(self, client, sample_email, sample_activity):
        """Test that duplicate signups are rejected"""
        # Arrange
        activity_name = sample_activity
        email = sample_email
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert first_response.status_code == 200
        
        # Act - Second signup with same email
        second_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert second_response.status_code == 400
        data = second_response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client, sample_email):
        """Test signup for non-existent activity"""
        # Arrange
        nonexistent_activity = "NonexistentActivity"
        email = sample_email
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_adds_participant(self, client, sample_email, sample_activity):
        """Test that participant is added to activity after signup"""
        # Arrange
        activity_name = sample_activity
        email = sample_email
        response_before = client.get("/activities")
        activities_before = response_before.json()
        participants_count_before = len(activities_before[activity_name]["participants"])
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response_after = client.get("/activities")
        activities_after = response_after.json()
        participants_after = activities_after[activity_name]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert email in participants_after
        assert len(participants_after) == participants_count_before + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, sample_activity):
        """Test successfully unregistering from an activity"""
        # Arrange
        activity_name = sample_activity
        test_email = "unregister_test@mergington.edu"
        
        # Act - Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]

    def test_unregister_not_registered(self, client, sample_activity):
        """Test unregistering when participant is not registered"""
        # Arrange
        activity_name = sample_activity
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        # Arrange
        nonexistent_activity = "NonexistentActivity"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_removes_participant(self, client, sample_activity):
        """Test that participant is removed after unregister"""
        # Arrange
        activity_name = sample_activity
        test_email = "remove_test@mergington.edu"
        
        # Act - Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        response_before = client.get("/activities")
        
        # Assert participant is present
        assert test_email in response_before.json()[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )
        response_after = client.get("/activities")
        
        # Assert
        assert unregister_response.status_code == 200
        assert test_email not in response_after.json()[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static files"""
        # Arrange
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert expected_redirect_path in response.headers["location"]
