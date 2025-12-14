"""
Unit tests for analyzer.py
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from prompt_master.analyzer import PromptAnalyzer


class TestPromptAnalyzer:
    """Test suite for PromptAnalyzer class"""

    @pytest.fixture
    def mock_api_key(self, monkeypatch):
        """Set up mock API key"""
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key-123")
        return "test-api-key-123"

    @pytest.fixture
    def analyzer(self, mock_api_key):
        """Create analyzer instance with mocked API"""
        with patch("google.generativeai.configure"), patch("google.generativeai.GenerativeModel"):
            return PromptAnalyzer(api_key=mock_api_key)

    def test_init_with_api_key(self):
        """Test initialization with explicit API key"""
        with (
            patch("google.generativeai.configure") as mock_configure,
            patch("google.generativeai.GenerativeModel"),
        ):
            analyzer = PromptAnalyzer(api_key="explicit-key")
            mock_configure.assert_called_once_with(api_key="explicit-key")
            assert analyzer.api_key == "explicit-key"

    def test_init_with_env_api_key(self, mock_api_key):
        """Test initialization with environment variable API key"""
        with (
            patch("google.generativeai.configure") as mock_configure,
            patch("google.generativeai.GenerativeModel"),
        ):
            analyzer = PromptAnalyzer()
            mock_configure.assert_called_once_with(api_key=mock_api_key)
            assert analyzer.api_key == mock_api_key

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key"""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API Key is missing"):
            PromptAnalyzer()

    def test_generation_config(self, analyzer):
        """Test generation configuration is set correctly"""
        assert analyzer.generation_config["temperature"] == 0.2
        assert analyzer.generation_config["response_mime_type"] == "application/json"

    def test_model_name_custom(self, mock_api_key):
        """Test custom model name initialization"""
        with (
            patch("google.generativeai.configure"),
            patch("google.generativeai.GenerativeModel") as mock_model,
        ):
            PromptAnalyzer(api_key=mock_api_key, model_name="gemini-pro")
            mock_model.assert_called_once()
            call_kwargs = mock_model.call_args[1]
            assert call_kwargs["model_name"] == "gemini-pro"

    @pytest.mark.asyncio
    async def test_analyze_async_success(self, analyzer):
        """Test successful async analysis"""
        mock_response = Mock()
        mock_response.text = json.dumps(
            {
                "score": 8,
                "summary": "Good prompt",
                "missing_rules": ["3"],
                "suggestions": [{"rule": "3", "advice": "Add format specification"}],
            }
        )

        analyzer.model.generate_content_async = AsyncMock(return_value=mock_response)

        result = await analyzer.analyze_async("Test prompt")

        assert result["score"] == 8
        assert result["summary"] == "Good prompt"
        assert "3" in result["missing_rules"]
        assert len(result["suggestions"]) == 1

    @pytest.mark.asyncio
    async def test_analyze_async_with_prompt_formatting(self, analyzer):
        """Test that prompt is formatted correctly in async call"""
        mock_response = Mock()
        mock_response.text = json.dumps(
            {"score": 5, "summary": "test", "missing_rules": [], "suggestions": []}
        )

        analyzer.model.generate_content_async = AsyncMock(return_value=mock_response)

        test_prompt = "Analyze this data"
        await analyzer.analyze_async(test_prompt)

        call_args = analyzer.model.generate_content_async.call_args[0][0]
        assert "Please analyze this prompt:" in call_args
        assert test_prompt in call_args

    @pytest.mark.asyncio
    async def test_analyze_async_error_handling(self, analyzer):
        """Test error handling in async analysis"""
        analyzer.model.generate_content_async = AsyncMock(side_effect=Exception("API Error"))

        result = await analyzer.analyze_async("Test prompt")

        assert result["score"] == 0
        assert result["summary"] == "Analysis failed"
        assert len(result["suggestions"]) == 1
        assert "API Error" in result["suggestions"][0]["advice"]

    def test_analyze_sync_success(self, analyzer):
        """Test successful sync analysis"""
        mock_response = Mock()
        mock_response.text = json.dumps(
            {
                "score": 7,
                "summary": "Decent prompt",
                "missing_rules": ["2", "8"],
                "suggestions": [
                    {"rule": "2", "advice": "Add a persona"},
                    {"rule": "8", "advice": "Specify length"},
                ],
            }
        )

        analyzer.model.generate_content = Mock(return_value=mock_response)

        result = analyzer.analyze_sync("Test prompt")

        assert result["score"] == 7
        assert result["summary"] == "Decent prompt"
        assert len(result["missing_rules"]) == 2
        assert len(result["suggestions"]) == 2

    def test_analyze_sync_with_generation_config(self, analyzer):
        """Test that generation config is passed in sync call"""
        mock_response = Mock()
        mock_response.text = json.dumps(
            {"score": 5, "summary": "test", "missing_rules": [], "suggestions": []}
        )

        analyzer.model.generate_content = Mock(return_value=mock_response)

        analyzer.analyze_sync("Test prompt")

        call_kwargs = analyzer.model.generate_content.call_args[1]
        assert "generation_config" in call_kwargs
        assert call_kwargs["generation_config"] == analyzer.generation_config

    def test_analyze_sync_error_handling(self, analyzer):
        """Test error handling in sync analysis"""
        analyzer.model.generate_content = Mock(side_effect=Exception("Connection timeout"))

        result = analyzer.analyze_sync("Test prompt")

        assert result["score"] == 0
        assert result["summary"] == "Analysis failed"
        assert result["missing_rules"] == []
        assert "Connection timeout" in result["suggestions"][0]["advice"]

    def test_analyze_sync_json_parse_error(self, analyzer):
        """Test handling of invalid JSON response in sync analysis"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON {{{}"

        analyzer.model.generate_content = Mock(return_value=mock_response)

        result = analyzer.analyze_sync("Test prompt")

        assert result["score"] == 0
        assert result["summary"] == "Analysis failed"

    @pytest.mark.asyncio
    async def test_analyze_async_json_parse_error(self, analyzer):
        """Test handling of invalid JSON response in async analysis"""
        mock_response = Mock()
        mock_response.text = "Not a JSON response"

        analyzer.model.generate_content_async = AsyncMock(return_value=mock_response)

        result = await analyzer.analyze_async("Test prompt")

        assert result["score"] == 0
        assert result["summary"] == "Analysis failed"

    def test_error_response_structure(self, analyzer):
        """Test error response has correct structure"""
        error_msg = "Test error message"
        result = analyzer._error_response(error_msg)

        assert "score" in result
        assert "summary" in result
        assert "missing_rules" in result
        assert "suggestions" in result
        assert result["score"] == 0
        assert result["summary"] == "Analysis failed"
        assert isinstance(result["missing_rules"], list)
        assert len(result["suggestions"]) == 1
        assert result["suggestions"][0]["rule"] == "System"
        assert result["suggestions"][0]["advice"] == error_msg
