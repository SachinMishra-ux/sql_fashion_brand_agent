"""
Automated CI Unit & Endpoint Tests for Maison Luxé AI Stylist Backend
Executes during GitHub Actions Stage 1 (CI Quality Gate) before any Docker build.
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend import auth

client = TestClient(app)


def test_auth_demo_users():
    """Verify pre-configured demo users and JWT token generation."""
    users = auth.get_demo_users_with_tokens()
    assert len(users) == 3

    # Check Priya Sharma
    priya = users[0]
    assert priya["name"] == "Priya Sharma"
    assert priya["loyalty_tier"] == "Platinum"
    assert "token" in priya and len(priya["token"]) > 20

    # Verify token payload
    decoded = auth.verify_token(priya["token"])
    assert decoded["sub"] == "1"
    assert decoded["name"] == "Priya Sharma"


def test_resolve_thread_id():
    """Verify thread ID resolution from username, user_id, and explicit thread_id."""
    assert auth.resolve_thread_id(username="Priya Sharma") == "user_thread_1"
    assert auth.resolve_thread_id(username="Aisha Khan") == "user_thread_2"
    assert auth.resolve_thread_id(username="Riya Verma") == "user_thread_3"
    assert auth.resolve_thread_id(user_id=1) == "user_thread_1"
    assert auth.resolve_thread_id(thread_id="custom_session_99") == "custom_session_99"


def test_get_demo_users_endpoint():
    """Verify GET /auth/users endpoint returns valid users with signed tokens."""
    res = client.get("/auth/users")
    assert res.status_code == 200
    data = res.json()
    assert "users" in data
    assert len(data["users"]) == 3
    for u in data["users"]:
        assert "token" in u
        assert "name" in u


def test_chat_endpoint_requires_auth():
    """Verify POST /chat rejects unauthenticated requests with HTTP 401/403."""
    res = client.post("/chat", json={"message": "Hello"})
    assert res.status_code in [401, 403]
