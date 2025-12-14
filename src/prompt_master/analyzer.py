import json
import os
from typing import Any

import google.generativeai as genai

from .system_prompts import AUDITOR_SYSTEM_PROMPT


class PromptAnalyzer:
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is missing. Set GEMINI_API_KEY environment variable.")

        genai.configure(api_key=self.api_key)

        self.generation_config = {"temperature": 0.2, "response_mime_type": "application/json"}

        self.model = genai.GenerativeModel(
            model_name=model_name, system_instruction=AUDITOR_SYSTEM_PROMPT
        )

    async def analyze_async(self, user_prompt: str) -> dict[str, Any]:
        """Non-blocking analysis for FastAPI."""
        try:
            response = await self.model.generate_content_async(
                f"Please analyze this prompt:\n\n{user_prompt}",
                generation_config=self.generation_config,
            )
            return json.loads(response.text)
        except Exception as e:
            return self._error_response(str(e))

    def analyze_sync(self, user_prompt: str) -> dict[str, Any]:
        """Blocking analysis for CLI."""
        try:
            response = self.model.generate_content(
                f"Please analyze this prompt:\n\n{user_prompt}",
                generation_config=self.generation_config,
            )
            return json.loads(response.text)
        except Exception as e:
            return self._error_response(str(e))

    def _error_response(self, error_msg: str) -> dict[str, Any]:
        return {
            "score": 0,
            "summary": "Analysis failed",
            "missing_rules": [],
            "suggestions": [{"rule": "System", "advice": error_msg}],
        }
