"""
Unit tests for api.py
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from prompt_master.api import app, get_analyzer


class TestAPI:
    """Test suite for FastAPI endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_analyzer(self):
        """Create mock analyzer"""
        analyzer = Mock()
        analyzer.analyze_async = AsyncMock()
        return analyzer

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "prompt-master"

    def test_app_metadata(self):
        """Test FastAPI app metadata"""
        assert app.title == "Prompt Master API"
        assert app.version == "0.3.0"
        assert "audit" in app.description.lower()

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_success(self, mock_analyzer_class, client):
        """Test successful analysis endpoint"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 9,
                "summary": "Excellent prompt",
                "missing_rules": [],
                "strengths": ["Clear", "Specific"],
                "suggestions": [],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        # Make request
        response = client.post(
            "/analyze", json={"prompt": "You are a Python expert. Write a function to sort a list."}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 9
        assert data["summary"] == "Excellent prompt"
        assert data["missing_rules"] == []
        assert len(data["strengths"]) == 2

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_with_custom_model(self, mock_analyzer_class, client):
        """Test analysis with custom model parameter"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 8,
                "summary": "Good",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Test prompt", "model": "gemini-pro"})

        assert response.status_code == 200
        mock_analyzer_class.assert_called_once_with(model_name="gemini-pro")

    def test_analyze_endpoint_missing_prompt(self, client):
        """Test analysis endpoint with missing prompt"""
        response = client.post("/analyze", json={})

        assert response.status_code == 422  # Validation error

    def test_analyze_endpoint_empty_prompt(self, client):
        """Test analysis endpoint with empty prompt"""
        response = client.post("/analyze", json={"prompt": ""})

        assert response.status_code == 422  # Validation error (min_length=5)

    def test_analyze_endpoint_short_prompt(self, client):
        """Test analysis endpoint with too short prompt"""
        response = client.post("/analyze", json={"prompt": "Hi"})

        assert response.status_code == 422  # Validation error (min_length=5)

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_default_model(self, mock_analyzer_class, client):
        """Test that default model is used when not specified"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 7,
                "summary": "OK",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Test prompt here"})

        assert response.status_code == 200
        mock_analyzer_class.assert_called_once_with(model_name="gemini-2.0-flash")

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_with_suggestions(self, mock_analyzer_class, client):
        """Test analysis response with suggestions"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 5,
                "summary": "Needs improvement",
                "missing_rules": ["2", "3"],
                "strengths": ["Clear"],
                "suggestions": [
                    {"rule": "2", "advice": "Add a persona"},
                    {"rule": "3", "advice": "Specify format"},
                ],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Simple prompt"})

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 5
        assert len(data["suggestions"]) == 2
        assert data["suggestions"][0]["rule"] == "2"
        assert "persona" in data["suggestions"][0]["advice"].lower()

    @patch("prompt_master.api.PromptAnalyzer")
    def test_get_analyzer_dependency_error(self, mock_analyzer_class):
        """Test get_analyzer raises HTTPException on ValueError"""
        mock_analyzer_class.side_effect = ValueError("API key missing")

        with pytest.raises(Exception) as exc_info:
            get_analyzer()

        assert "API key missing" in str(exc_info.value)

    def test_analyze_request_validation(self):
        """Test AnalyzeRequest model validation"""
        from prompt_master.api import AnalyzeRequest

        # Valid request
        request = AnalyzeRequest(prompt="Valid prompt here")
        assert request.prompt == "Valid prompt here"
        assert request.model == "gemini-2.0-flash"  # default

        # Custom model
        request = AnalyzeRequest(prompt="Test prompt", model="gemini-pro")
        assert request.model == "gemini-pro"

    def test_analyze_response_model(self):
        """Test AnalyzeResponse model structure"""
        from prompt_master.api import AnalyzeResponse, Suggestion

        response = AnalyzeResponse(
            score=8,
            summary="Good prompt",
            missing_rules=["3"],
            strengths=["Clear", "Specific"],
            suggestions=[Suggestion(rule="3", advice="Add format")],
        )

        assert response.score == 8
        assert response.summary == "Good prompt"
        assert len(response.suggestions) == 1
        assert response.suggestions[0].rule == "3"

    def test_suggestion_model(self):
        """Test Suggestion model structure"""
        from prompt_master.api import Suggestion

        suggestion = Suggestion(rule="5", advice="Add context")
        assert suggestion.rule == "5"
        assert suggestion.advice == "Add context"

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_long_prompt(self, mock_analyzer_class, client):
        """Test analysis with a long prompt"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 10,
                "summary": "Perfect",
                "missing_rules": [],
                "strengths": ["Everything"],
                "suggestions": [],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        long_prompt = "A" * 5000  # 5000 character prompt
        response = client.post("/analyze", json={"prompt": long_prompt})

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 10

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "paths" in schema
        assert "/analyze" in schema["paths"]
        assert "/health" in schema["paths"]

    @patch("prompt_master.api.PromptAnalyzer")
    def test_analyze_endpoint_unicode_prompt(self, mock_analyzer_class, client):
        """Test analysis with unicode characters in prompt"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 7,
                "summary": "Good",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Analysez ce texte: café, naïve, 你好"})

        assert response.status_code == 200
