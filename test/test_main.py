"""
Essential main app tests only
"""

import pytest
from fastapi import status


class TestMain:
    """Core app functionality"""
    
    def test_health_check(self, client):
        """Test health endpoint works"""
        response = client.get("/healthy")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}