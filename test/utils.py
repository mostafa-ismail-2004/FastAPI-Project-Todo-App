"""
Test utilities for FastAPI Todo App
Provides shared fixtures, database setup, and helper functions for testing
"""

import os

"""
Test utilities for FastAPI Todo App
Provides shared fixtures, database setup, and helper functions for testing
"""

import os

# Set testing environment BEFORE any other imports
os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-secure"
os.environ["DATABASE_URL"] = "sqlite:///./test_database.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base, get_db, engine, SessionLocal  # Import the same engine and SessionLocal
from models import Users, Todos
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta, datetime, timezone
from typing import Optional
import tempfile

# Import main after setting environment
import main

# Use the same database configuration as main app
TestingSessionLocal = SessionLocal  # Use the same SessionLocal from database.py

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Test JWT configuration (use environment variable like the main app)
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only-not-secure")
ALGORITHM = 'HS256'


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    # Override the database dependency
    main.app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(main.app) as test_client:
        yield test_client
    
    # Clean up dependency overrides
    main.app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    user = Users(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_active=True,
        role="user",
        phone_number="1234567890"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user in the database"""
    admin = Users(
        username="adminuser",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password=bcrypt_context.hash("adminpassword"),
        is_active=True,
        role="admin",
        phone_number="9876543210"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_todo(db_session, test_user):
    """Create a test todo in the database"""
    todo = Todos(
        title="Test Todo",
        description="This is a test todo",
        priority=1,
        complete=False,
        owner_id=test_user.id
    )
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo


def create_access_token(username: str, user_id: int, role: str, expires_delta: Optional[timedelta] = None):
    """Create JWT access token for testing"""
    encode = {'sub': username, 'id': user_id, 'role': role}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def user_token(test_user):
    """Generate JWT token for test user"""
    return create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        role=test_user.role
    )


@pytest.fixture
def admin_token(test_admin):
    """Generate JWT token for test admin"""
    return create_access_token(
        username=test_admin.username,
        user_id=test_admin.id,
        role=test_admin.role
    )


def get_auth_headers(token: str):
    """Get authorization headers with Bearer token"""
    return {"Authorization": f"Bearer {token}"}


class TestDataFactory:
    """Factory class for creating test data"""
    
    @staticmethod
    def create_user_data(
        username="newuser",
        email="newuser@example.com",
        first_name="New",
        last_name="User",
        password="newpassword",
        role="user",
        phone_number="5555555555"
    ):
        return {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "role": role,
            "phone_number": phone_number
        }
    
    @staticmethod
    def create_todo_data(
        title="New Todo",
        description="New todo description",
        priority=1,
        complete=False
    ):
        return {
            "title": title,
            "description": description,
            "priority": priority,
            "complete": complete
        }
    
    @staticmethod
    def create_login_data(username="testuser", password="testpassword"):
        return {
            "username": username,
            "password": password
        }


# Cleanup function for manual database cleanup if needed
def cleanup_test_database():
    """Manually clean up test database if needed"""
    try:
        if os.path.exists("test_database.db"):
            os.remove("test_database.db")
    except OSError:
        pass


# Session-scoped cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """Clean up after all tests are done"""
    yield
    cleanup_test_database()
