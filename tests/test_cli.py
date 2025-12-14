"""
Unit tests for cli.py
"""

import json
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from prompt_master.cli import _print_rich_report, app


class TestCLI:
    """Test suite for CLI commands"""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()

    @pytest.fixture
    def sample_analysis_result(self):
        """Sample analysis result"""
        return {
            "score": 8,
            "summary": "Good prompt with minor improvements needed",
            "missing_rules": ["3", "8"],
            "strengths": ["Clear", "Direct"],
            "suggestions": [
                {"rule": "3", "advice": "Specify output format"},
                {"rule": "8", "advice": "Add length constraint"},
            ],
        }

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_with_text(self, mock_analyzer_class, runner):
        """Test analyze command with direct text input"""
        # Setup mock
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(
            return_value={"score": 9, "summary": "Excellent", "suggestions": []}
        )
        mock_analyzer_class.return_value = mock_instance

        result = runner.invoke(app, ["analyze", "Test prompt here"])

        assert result.exit_code == 0
        mock_instance.analyze_sync.assert_called_once_with("Test prompt here")

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_with_custom_model(self, mock_analyzer_class, runner):
        """Test analyze command with custom model"""
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(
            return_value={"score": 8, "summary": "Good", "suggestions": []}
        )
        mock_analyzer_class.return_value = mock_instance

        result = runner.invoke(app, ["analyze", "Test prompt", "--model", "gemini-pro"])

        assert result.exit_code == 0
        mock_analyzer_class.assert_called_once_with(model_name="gemini-pro")

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_json_output(self, mock_analyzer_class, runner, sample_analysis_result):
        """Test analyze command with JSON output"""
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(return_value=sample_analysis_result)
        mock_analyzer_class.return_value = mock_instance

        result = runner.invoke(app, ["analyze", "Test prompt", "--json-output"])

        assert result.exit_code == 0
        # Parse output as JSON
        output_data = json.loads(result.stdout)
        assert output_data["score"] == 8
        assert output_data["summary"] == sample_analysis_result["summary"]

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_missing_api_key(self, mock_analyzer_class, runner):
        """Test analyze command fails gracefully without API key"""
        mock_analyzer_class.side_effect = ValueError("API Key is missing")

        result = runner.invoke(app, ["analyze", "Test prompt"])

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_default_model(self, mock_analyzer_class, runner):
        """Test analyze command uses default model"""
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(
            return_value={"score": 5, "summary": "OK", "suggestions": []}
        )
        mock_analyzer_class.return_value = mock_instance

        result = runner.invoke(app, ["analyze", "Test prompt"])

        assert result.exit_code == 0
        mock_analyzer_class.assert_called_once_with(model_name="gemini-2.0-flash")

    @patch("uvicorn.run")
    def test_serve_command_default_settings(self, mock_uvicorn, runner):
        """Test serve command with default settings"""
        result = runner.invoke(app, ["serve"])

        assert result.exit_code == 0
        mock_uvicorn.assert_called_once_with(
            "prompt_master.api:app", host="127.0.0.1", port=8000, reload=False
        )

    @patch("uvicorn.run")
    def test_serve_command_custom_host_port(self, mock_uvicorn, runner):
        """Test serve command with custom host and port"""
        result = runner.invoke(app, ["serve", "--host", "0.0.0.0", "--port", "9000"])

        assert result.exit_code == 0
        mock_uvicorn.assert_called_once_with(
            "prompt_master.api:app", host="0.0.0.0", port=9000, reload=False
        )

    @patch("uvicorn.run")
    def test_serve_command_with_reload(self, mock_uvicorn, runner):
        """Test serve command with reload enabled"""
        result = runner.invoke(app, ["serve", "--reload"])

        assert result.exit_code == 0
        call_kwargs = mock_uvicorn.call_args[1]
        assert call_kwargs["reload"] is True

    def test_print_rich_report_high_score(self, sample_analysis_result):
        """Test rich report printing with high score"""
        sample_analysis_result["score"] = 9

        # Should not raise any exceptions
        _print_rich_report(sample_analysis_result)

    def test_print_rich_report_medium_score(self, sample_analysis_result):
        """Test rich report printing with medium score"""
        sample_analysis_result["score"] = 6

        # Should not raise any exceptions
        _print_rich_report(sample_analysis_result)

    def test_print_rich_report_low_score(self, sample_analysis_result):
        """Test rich report printing with low score"""
        sample_analysis_result["score"] = 3

        # Should not raise any exceptions
        _print_rich_report(sample_analysis_result)

    def test_print_rich_report_with_suggestions(self, sample_analysis_result):
        """Test rich report includes suggestions"""
        # Should not raise any exceptions and format suggestions
        _print_rich_report(sample_analysis_result)

    def test_print_rich_report_without_suggestions(self):
        """Test rich report without suggestions"""
        data = {"score": 10, "summary": "Perfect prompt", "suggestions": []}

        # Should not raise any exceptions
        _print_rich_report(data)

    def test_print_rich_report_missing_fields(self):
        """Test rich report with missing optional fields"""
        data = {"score": 5, "summary": "OK"}

        # Should handle missing suggestions gracefully
        _print_rich_report(data)

    @patch("prompt_master.cli.PromptAnalyzer")
    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("os.path.exists", return_value=True)
    def test_analyze_command_file_not_readable(
        self, mock_exists, mock_file, mock_analyzer_class, runner
    ):
        """Test analyze command with unreadable file"""
        result = runner.invoke(app, ["analyze", "nonexistent.txt"])

        # Should fail with error
        assert result.exit_code != 0

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_with_multiline_prompt(self, mock_analyzer_class, runner):
        """Test analyze command with multiline prompt"""
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(
            return_value={"score": 8, "summary": "Good", "suggestions": []}
        )
        mock_analyzer_class.return_value = mock_instance

        multiline_prompt = "Line 1\nLine 2\nLine 3"
        result = runner.invoke(app, ["analyze", multiline_prompt])

        assert result.exit_code == 0
        mock_instance.analyze_sync.assert_called_once_with(multiline_prompt)

    @patch("prompt_master.cli.PromptAnalyzer")
    def test_analyze_command_with_special_characters(self, mock_analyzer_class, runner):
        """Test analyze command with special characters"""
        mock_instance = Mock()
        mock_instance.analyze_sync = Mock(
            return_value={"score": 7, "summary": "Good", "suggestions": []}
        )
        mock_analyzer_class.return_value = mock_instance

        prompt_with_special = "Test with émojis 🚀 and symbols @#$%"
        result = runner.invoke(app, ["analyze", prompt_with_special])

        assert result.exit_code == 0

    def test_app_help_text(self, runner):
        """Test CLI help text"""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Prompt Master" in result.stdout
        assert "analyze" in result.stdout
        assert "serve" in result.stdout

    def test_analyze_help_text(self, runner):
        """Test analyze command help text"""
        result = runner.invoke(app, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "prompt" in result.stdout.lower()
        assert "model" in result.stdout.lower()

    def test_serve_help_text(self, runner):
        """Test serve command help text"""
        result = runner.invoke(app, ["serve", "--help"])

        assert result.exit_code == 0
        assert "host" in result.stdout.lower()
        assert "port" in result.stdout.lower()
        assert "reload" in result.stdout.lower()
