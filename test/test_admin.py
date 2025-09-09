"""
Essential admin tests only
"""

import pytest
from fastapi import status
from .utils import get_auth_headers


class TestAdmin:
    """Core admin functionality"""
    
    def test_admin_get_all_todos(self, client, admin_token):
        """Test admin can get all todos"""
        headers = get_auth_headers(admin_token)
        response = client.get("/admin/todos", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_user_cannot_access_admin(self, client, user_token):
        """Test regular user cannot access admin endpoints"""
        headers = get_auth_headers(user_token)
        response = client.get("/admin/todos", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_delete_todo(self, client, admin_token, test_todo):
        """Test admin can delete any todo"""
        headers = get_auth_headers(admin_token)
        response = client.delete(f"/admin/todos/{test_todo.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
