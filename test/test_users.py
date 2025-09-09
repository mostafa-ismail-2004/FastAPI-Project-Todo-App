"""Minimal user endpoint tests"""

import pytest
from fastapi import status
from .utils import get_auth_headers


def test_get_user_info(client, user_token):
    """Test getting user info"""
    headers = get_auth_headers(user_token)
    response = client.get("/users/user-info", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_change_password(client, user_token):
    """Test changing password"""
    headers = get_auth_headers(user_token)
    response = client.post(
        "/users/change-password?old_password=testpassword&new_password=newpassword123",
        headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_phone_number(client, user_token):
    """Test changing phone number"""
    headers = get_auth_headers(user_token)
    response = client.post(
        "/users/change-phone-number?new_phone_number=9876543210",
        headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT