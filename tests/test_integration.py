"""
Integration tests for the full prompt_master workflow
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from prompt_master.analyzer import PromptAnalyzer
from prompt_master.api import app


class TestIntegration:
    """Integration tests for end-to-end workflows"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_gemini_successful_response(self):
        """Mock successful Gemini response"""
        return {
            "score": 8,
            "summary": "Strong prompt with minor improvements needed",
            "missing_rules": ["8"],
            "strengths": [
                "Clear persona definition",
                "Specific task description",
                "Good use of context",
            ],
            "suggestions": [
                {
                    "rule": "8",
                    "advice": "Consider adding length constraints like 'in 200 words or less'",
                }
            ],
        }

    @patch("prompt_master.api.PromptAnalyzer")
    def test_full_api_workflow(self, mock_analyzer_class, client, mock_gemini_successful_response):
        """Test complete API request-response workflow"""
        # Setup
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(return_value=mock_gemini_successful_response)
        mock_analyzer_class.return_value = mock_instance

        # Execute
        response = client.post(
            "/analyze",
            json={
                "prompt": "You are a Python expert. Write a function to sort a list.",
                "model": "gemini-2.0-flash",
            },
        )

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 8
        assert len(data["strengths"]) == 3
        assert len(data["suggestions"]) == 1
        assert data["missing_rules"] == ["8"]

    @patch("prompt_master.api.PromptAnalyzer")
    def test_api_handles_poor_prompt(self, mock_analyzer_class, client):
        """Test API correctly identifies and reports poor prompts"""
        poor_response = {
            "score": 3,
            "summary": "Prompt needs significant improvement",
            "missing_rules": ["1", "2", "3", "4", "6", "8"],
            "strengths": [],
            "suggestions": [
                {"rule": "1", "advice": "Be more specific and clear"},
                {"rule": "2", "advice": "Add a persona or role"},
                {"rule": "3", "advice": "Specify output format"},
            ],
        }

        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(return_value=poor_response)
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "do something"})

        assert response.status_code == 200
        data = response.json()
        assert data["score"] <= 4
        assert len(data["missing_rules"]) >= 5
        assert len(data["suggestions"]) >= 3

    @patch("prompt_master.api.PromptAnalyzer")
    def test_api_handles_excellent_prompt(self, mock_analyzer_class, client):
        """Test API correctly identifies excellent prompts"""
        excellent_response = {
            "score": 10,
            "summary": "Excellent prompt following all best practices",
            "missing_rules": [],
            "strengths": [
                "Perfect clarity and specificity",
                "Well-defined persona",
                "Clear format requirements",
                "Appropriate context",
                "Strong action verbs",
                "Length specified",
            ],
            "suggestions": [],
        }

        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(return_value=excellent_response)
        mock_analyzer_class.return_value = mock_instance

        response = client.post(
            "/analyze",
            json={
                "prompt": """You are a senior Python developer with expertise in algorithms.
                
                Task: Implement a binary search function.
                Format: Return clean, documented Python code with type hints.
                Length: Keep under 30 lines.
                Context: This will be used in a production system requiring O(log n) performance.
                
                Based on the above requirements, write the implementation."""
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 10
        assert len(data["missing_rules"]) == 0
        assert len(data["strengths"]) >= 5

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_analyzer_initialization_workflow(self, mock_model_class, mock_configure):
        """Test analyzer initialization with proper configuration"""
        # Setup
        mock_model = Mock()
        mock_model_class.return_value = mock_model

        # Execute
        PromptAnalyzer(api_key="test-key-123", model_name="gemini-pro")

        # Verify
        mock_configure.assert_called_once_with(api_key="test-key-123")
        mock_model_class.assert_called_once()

        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs["model_name"] == "gemini-pro"
        assert "system_instruction" in call_kwargs

    @patch("prompt_master.api.PromptAnalyzer")
    def test_api_error_recovery(self, mock_analyzer_class, client):
        """Test that API handles analyzer errors gracefully"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 0,
                "summary": "Analysis failed",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [{"rule": "System", "advice": "API connection timeout"}],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Test prompt"})

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 0
        assert "failed" in data["summary"].lower()

    @patch("prompt_master.api.PromptAnalyzer")
    def test_multiple_consecutive_requests(self, mock_analyzer_class, client):
        """Test handling of multiple consecutive API requests"""
        responses = [
            {
                "score": 7,
                "summary": "Good",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [],
            },
            {"score": 5, "summary": "OK", "missing_rules": [], "strengths": [], "suggestions": []},
            {
                "score": 9,
                "summary": "Excellent",
                "missing_rules": [],
                "strengths": [],
                "suggestions": [],
            },
        ]

        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(side_effect=responses)
        mock_analyzer_class.return_value = mock_instance

        # Make multiple requests
        scores = []
        for i in range(3):
            response = client.post("/analyze", json={"prompt": f"Test prompt {i}"})
            assert response.status_code == 200
            scores.append(response.json()["score"])

        assert scores == [7, 5, 9]

    @patch("prompt_master.api.PromptAnalyzer")
    def test_different_model_selections(self, mock_analyzer_class, client):
        """Test that different models can be selected"""
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

        models = ["gemini-2.5-flash", "gemini-pro", "gemini-2.5-pro"]

        for model in models:
            response = client.post("/analyze", json={"prompt": "Test prompt", "model": model})
            assert response.status_code == 200

        # Verify all models were tried
        assert mock_analyzer_class.call_count == len(models)

    @patch("prompt_master.api.PromptAnalyzer")
    def test_api_response_structure_completeness(self, mock_analyzer_class, client):
        """Test that API responses have all required fields"""
        mock_instance = Mock()
        mock_instance.analyze_async = AsyncMock(
            return_value={
                "score": 7,
                "summary": "Test summary",
                "missing_rules": ["1", "2"],
                "strengths": ["Good structure"],
                "suggestions": [
                    {"rule": "1", "advice": "Test advice 1"},
                    {"rule": "2", "advice": "Test advice 2"},
                ],
            }
        )
        mock_analyzer_class.return_value = mock_instance

        response = client.post("/analyze", json={"prompt": "Tests with more than 5 characters"})
        if response.status_code != 200:
            print("Validation errors:", response.json())
        assert response.status_code == 200
        data = response.json()

        # Check all required fields are present
        assert "score" in data
        assert "summary" in data
        assert "missing_rules" in data
        assert "strengths" in data
        assert "suggestions" in data

        # Check types
        assert isinstance(data["score"], int)
        assert isinstance(data["summary"], str)
        assert isinstance(data["missing_rules"], list)
        assert isinstance(data["strengths"], list)
        assert isinstance(data["suggestions"], list)

    def test_health_check_integration(self, client):
        """Test health check endpoint in integration"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
