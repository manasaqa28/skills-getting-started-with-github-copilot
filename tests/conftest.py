"""Pytest configuration and fixtures for FastAPI tests"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Fixture providing a sample email for tests"""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity():
    """Fixture providing a sample activity name"""
    return "Chess Club"
