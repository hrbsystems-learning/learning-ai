"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ.update({
        "ENVIRONMENT": "test",
        "OPENAI_API_KEY": "test-openai-key",
        "CUSTOMER_NAME": "test-customer",
        "LOG_LEVEL": "DEBUG",
        "CREWAI_TELEMETRY_OPT_OUT": "true"
    })


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with patch("langchain_openai.ChatOpenAI") as mock:
        mock_instance = Mock()
        mock_instance.run.return_value = "Mocked LLM response"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_crew():
    """Mock CrewAI crew."""
    with patch("crewai.Crew") as mock:
        mock_instance = Mock()
        mock_instance.kickoff.return_value = "Mocked crew result"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "text": "This is sample text for testing",
        "numbers": [1, 2, 3, 4, 5],
        "metadata": {
            "source": "test",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def sample_analysis_result():
    """Sample analysis result for testing."""
    return {
        "summary": "This is a test analysis",
        "key_insights": ["Insight 1", "Insight 2"],
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "confidence": 0.85
    }
