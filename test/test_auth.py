"""Minimal auth endpoint tests"""

import pytest
from fastapi import status
from .utils import get_auth_headers


def test_register_user(client):
    """Test user registration"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com", 
        "first_name": "New",
        "last_name": "User",
        "password": "newpassword",
        "role": "user",
        "phone_number": "1234567890"
    }
    
    response = client.post("/auth/new-user", json=user_data)  # Using correct endpoint
    assert response.status_code == status.HTTP_201_CREATED


def test_login_success(client, test_user):
    """Test successful login"""
    login_data = {"username": "testuser", "password": "testpassword"}
    
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_fail(client, test_user):
    """Test login with wrong credentials"""
    # Test with existing user but wrong password (should return 401)
    login_data = {"username": "testuser", "password": "wrongpassword"}
    
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED