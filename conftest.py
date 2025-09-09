"""
Pytest configuration and shared fixtures for FastAPI Todo App tests
This file contains test configuration and fixtures that are available to all test files
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set testing environment before any imports
os.environ["TESTING"] = "1"

# Import test utilities and fixtures
from test.utils import (
    db_session,
    client,
    test_user,
    test_admin,
    test_todo,
    user_token,
    admin_token,
    cleanup_after_tests,
)

# Re-export fixtures so they're available to all test modules
__all__ = [
    "db_session",
    "client", 
    "test_user",
    "test_admin",
    "test_todo",
    "user_token",
    "admin_token",
]


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Automatically run before each test to ensure clean environment
    """
    # Ensure testing environment is set
    os.environ["TESTING"] = "1"
    
    # Clear any cached modules that might interfere
    if "main" in sys.modules:
        # Reset any module-level state if needed
        pass
    
    yield
    
    # Cleanup after test
    # Any additional cleanup can go here


@pytest.fixture(scope="session")
def test_database_url():
    """
    Provide test database URL
    """
    return "sqlite:///./test_database.db"


def pytest_configure(config):
    """
    Pytest configuration hook - runs once at start of test session
    """
    # Ensure we're in testing mode
    os.environ["TESTING"] = "1"
    
    # Add custom markers
    config.addinivalue_line(
        "markers", "auth: mark test as related to authentication"
    )
    config.addinivalue_line(
        "markers", "todos: mark test as related to todos functionality"  
    )
    config.addinivalue_line(
        "markers", "admin: mark test as related to admin functionality"
    )
    config.addinivalue_line(
        "markers", "users: mark test as related to user management"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_unconfigure(config):
    """
    Pytest cleanup hook - runs once at end of test session
    """
    # Clean up test database file
    test_db_path = Path("test_database.db")
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except OSError:
            pass  # Ignore if file can't be deleted


@pytest.fixture(scope="function")
def isolated_test():
    """
    Fixture for tests that need complete isolation
    """
    # Setup
    original_env = os.environ.copy()
    
    yield
    
    # Restore environment
    os.environ.clear()
    os.environ.update(original_env)


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """
    Modify test collection - add markers based on test location/name
    """
    for item in items:
        # Add markers based on test file names
        if "test_auth" in item.fspath.basename:
            item.add_marker(pytest.mark.auth)
        elif "test_todos" in item.fspath.basename:
            item.add_marker(pytest.mark.todos)
        elif "test_admin" in item.fspath.basename:
            item.add_marker(pytest.mark.admin)
        elif "test_users" in item.fspath.basename:
            item.add_marker(pytest.mark.users)
        elif "test_main" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests based on name patterns
        if "flow" in item.name.lower() or "integration" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark all tests as unit by default unless they're integration
        if not any(marker.name == "integration" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# Custom pytest hooks for better test output
def pytest_runtest_setup(item):
    """
    Called before each test runs
    """
    # Ensure testing environment for each test
    os.environ["TESTING"] = "1"


def pytest_runtest_teardown(item, nextitem):
    """
    Called after each test completes
    """
    # Any per-test cleanup
    pass


def pytest_sessionstart(session):
    """
    Called after session has been created
    """
    print("\n🧪 Starting FastAPI Todo App Test Suite")
    print("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after test session finishes
    """
    print("\n" + "=" * 50)
    print(f"✅ Test Session Complete - Exit Status: {exitstatus}")
    
    # Clean up any remaining test artifacts
    cleanup_artifacts = [
        "test_database.db",
        "test_database.db-journal",
        ".coverage",
    ]
    
    for artifact in cleanup_artifacts:
        artifact_path = Path(artifact)
        if artifact_path.exists():
            try:
                artifact_path.unlink()
                print(f"🗑️  Cleaned up: {artifact}")
            except OSError:
                print(f"⚠️  Could not clean up: {artifact}")


# Environment variable management for tests
@pytest.fixture(scope="function")
def temp_env_var():
    """
    Fixture for temporarily setting environment variables during tests
    """
    original_values = {}
    
    def set_env(key, value):
        if key in os.environ:
            original_values[key] = os.environ[key]
        os.environ[key] = value
    
    yield set_env
    
    # Restore original values
    for key, original_value in original_values.items():
        os.environ[key] = original_value
    
    # Remove any keys that weren't originally set
    for key in os.environ.copy():
        if key not in original_values and key != "TESTING":
            del os.environ[key]
