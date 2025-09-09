"""Minimal todo endpoint tests"""

import pytest
from fastapi import status
from .utils import get_auth_headers


def test_get_todos(client, user_token):
    """Test getting todos"""
    headers = get_auth_headers(user_token)
    response = client.get("/todos", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_create_todo(client, user_token):
    """Test creating a todo"""
    headers = get_auth_headers(user_token)
    todo_data = {
        "title": "Test Todo",
        "description": "Test description",
        "priority": 1
    }
    
    response = client.post("/todos", json=todo_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED


def test_get_todo_by_id(client, user_token, test_todo):
    """Test getting specific todo"""
    headers = get_auth_headers(user_token)
    response = client.get(f"/todos/{test_todo.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_update_todo(client, user_token, test_todo):
    """Test updating a todo"""
    headers = get_auth_headers(user_token)
    update_data = {
        "title": "Updated Todo",
        "description": "Updated description",
        "priority": 2,
        "complete": True
    }
    
    response = client.put(f"/todos/{test_todo.id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_delete_todo(client, user_token, test_todo):
    """Test deleting a todo"""
    headers = get_auth_headers(user_token)
    response = client.delete(f"/todos/{test_todo.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT