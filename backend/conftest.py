"""Pytest configuration for functional tests."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture(autouse=True)
def mock_services():
    """Mock all external services for functional tests."""
    # We'll use this to mock game_service, clue_service, dialogue_service
    # The actual mocking will be done in individual test files
    pass

