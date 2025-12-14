"""
Pytest configuration and shared fixtures
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_prompt_examples():
    """Sample prompts for testing"""
    return {
        "good_prompt": """You are an expert Python developer. 
        Write a function to calculate the Fibonacci sequence up to n terms.
        The output should be a list of integers.
        Keep the implementation concise and include docstrings.""",
        "bad_prompt": "Write code for Fibonacci",
        "medium_prompt": """Write a Python function for Fibonacci sequence.
        Return a list.""",
        "perfect_prompt": """You are a senior Python engineer with 10 years of experience.
        
        Task: Create a function that generates the Fibonacci sequence.
        
        Requirements:
        - Accept parameter n (number of terms)
        - Return a list of integers
        - Include comprehensive docstring
        - Add type hints
        - Keep implementation under 20 lines
        - Use efficient algorithm
        
        Based on the requirements above, write clean, production-ready code.""",
        "empty_prompt": "",
        "minimal_prompt": "Hi",
        "unicode_prompt": "Écrivez une fonction Python pour calculer π avec précision 🥧",
        "multiline_prompt": """Line 1: Introduction
        Line 2: Main task
        Line 3: Requirements
        Line 4: Conclusion""",
    }


@pytest.fixture
def sample_api_response():
    """Sample API response structure"""
    return {
        "score": 8,
        "summary": "Good prompt with room for improvement",
        "missing_rules": ["3", "8"],
        "strengths": ["Clear task definition", "Specific role assignment"],
        "suggestions": [
            {
                "rule": "3",
                "advice": "Specify the exact output "
                "format (e.g., 'Return as JSON', 'Format as table')",
            },
            {
                "rule": "8",
                "advice": "Add length constraints (e.g., 'Keep response under 200 words')",
            },
        ],
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response format"""

    class MockResponse:
        def __init__(self, text):
            self.text = text

    return MockResponse


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables before each test"""
    # This fixture runs automatically before each test
    # Ensure no API keys leak between tests
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


@pytest.fixture
def temp_prompt_file(tmp_path):
    """Create a temporary prompt file for testing"""
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("This is a test prompt from a file")
    return prompt_file
