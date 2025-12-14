"""
Unit tests for system_prompts.py
"""

from prompt_master.system_prompts import AUDITOR_SYSTEM_PROMPT


class TestSystemPrompts:
    """Test suite for system prompts"""

    def test_auditor_system_prompt_exists(self):
        """Test that AUDITOR_SYSTEM_PROMPT is defined"""
        assert AUDITOR_SYSTEM_PROMPT is not None
        assert isinstance(AUDITOR_SYSTEM_PROMPT, str)
        assert len(AUDITOR_SYSTEM_PROMPT) > 0

    def test_auditor_system_prompt_contains_role(self):
        """Test that prompt defines the auditor role"""
        assert "expert" in AUDITOR_SYSTEM_PROMPT.lower()
        assert "auditor" in AUDITOR_SYSTEM_PROMPT.lower()

    def test_auditor_system_prompt_mentions_golden_rules(self):
        """Test that prompt mentions the 10 Golden Rules"""
        assert "10" in AUDITOR_SYSTEM_PROMPT
        assert "golden" in AUDITOR_SYSTEM_PROMPT.lower() or "rules" in AUDITOR_SYSTEM_PROMPT.lower()

    def test_auditor_system_prompt_specifies_json_output(self):
        """Test that prompt specifies JSON output format"""
        assert "json" in AUDITOR_SYSTEM_PROMPT.lower()

    def test_auditor_system_prompt_contains_all_rules(self):
        """Test that all 10 rules are mentioned"""
        rules_keywords = [
            "clear",
            "persona",
            "format",
            "context priority",
            "contextual data",
            "action verbs",
            "context anchors",
            "length",
            "iterative",
            "fact checking",
        ]

        prompt_lower = AUDITOR_SYSTEM_PROMPT.lower()

        # At least 8 out of 10 keywords should be present (allowing some variation)
        found_count = sum(1 for keyword in rules_keywords if keyword in prompt_lower)
        assert found_count >= 8, f"Only {found_count}/10 rule keywords found"

    def test_auditor_system_prompt_output_schema(self):
        """Test that prompt includes expected output schema fields"""
        required_fields = ["score", "summary", "missing_rules", "suggestions"]

        for field in required_fields:
            assert field in AUDITOR_SYSTEM_PROMPT, f"Field '{field}' not found in prompt"

    def test_auditor_system_prompt_mentions_advice(self):
        """Test that prompt includes advice field in suggestions"""
        assert "advice" in AUDITOR_SYSTEM_PROMPT

    def test_auditor_system_prompt_score_range(self):
        """Test that prompt specifies score range"""
        # Should mention 0-10 or similar
        assert "0" in AUDITOR_SYSTEM_PROMPT or "zero" in AUDITOR_SYSTEM_PROMPT.lower()
        assert "10" in AUDITOR_SYSTEM_PROMPT

    def test_auditor_system_prompt_mentions_llm(self):
        """Test that prompt mentions Large Language Model or LLM"""
        prompt_upper = AUDITOR_SYSTEM_PROMPT.upper()
        assert "LLM" in prompt_upper or "LARGE LANGUAGE MODEL" in prompt_upper

    def test_auditor_system_prompt_is_multiline(self):
        """Test that prompt is formatted across multiple lines"""
        lines = AUDITOR_SYSTEM_PROMPT.split("\n")
        assert len(lines) > 10, "Prompt should be formatted across multiple lines"

    def test_auditor_system_prompt_has_structured_sections(self):
        """Test that prompt has clear sections with headers"""
        # Should have section markers like ###
        assert "###" in AUDITOR_SYSTEM_PROMPT or "**" in AUDITOR_SYSTEM_PROMPT

    def test_auditor_system_prompt_rule_numbers(self):
        """Test that rules are numbered 1-10"""
        for i in range(1, 11):
            assert str(i) in AUDITOR_SYSTEM_PROMPT, f"Rule number {i} not found"

    def test_auditor_system_prompt_minimal_length(self):
        """Test that prompt is sufficiently detailed"""
        # Should be at least 1000 characters to be comprehensive
        assert len(AUDITOR_SYSTEM_PROMPT) >= 1000

    def test_auditor_system_prompt_mentions_strengths(self):
        """Test that prompt includes strengths field"""
        assert "strengths" in AUDITOR_SYSTEM_PROMPT.lower()

    def test_auditor_system_prompt_critical_tone(self):
        """Test that prompt encourages critical analysis"""
        prompt_lower = AUDITOR_SYSTEM_PROMPT.lower()
        assert "critical" in prompt_lower or "strict" in prompt_lower

    def test_auditor_system_prompt_json_structure_example(self):
        """Test that prompt includes JSON structure with curly braces"""
        assert "{" in AUDITOR_SYSTEM_PROMPT
        assert "}" in AUDITOR_SYSTEM_PROMPT

    def test_auditor_system_prompt_specific_rules_content(self):
        """Test that specific rule content is present"""
        # Rule 1: Clear and Direct
        assert "clear" in AUDITOR_SYSTEM_PROMPT.lower()
        assert "direct" in AUDITOR_SYSTEM_PROMPT.lower()

        # Rule 2: Persona
        assert "persona" in AUDITOR_SYSTEM_PROMPT.lower() or "role" in AUDITOR_SYSTEM_PROMPT.lower()

        # Rule 3: Format
        assert "format" in AUDITOR_SYSTEM_PROMPT.lower()

        # Rule 6: Action verbs
        assert "action" in AUDITOR_SYSTEM_PROMPT.lower() and "verb" in AUDITOR_SYSTEM_PROMPT.lower()

    def test_auditor_system_prompt_no_typos_in_keywords(self):
        """Test that critical keywords are spelled correctly"""
        # Check for common typos
        assert "anaysis" not in AUDITOR_SYSTEM_PROMPT.lower()  # should be "analysis"
        assert "promt" not in AUDITOR_SYSTEM_PROMPT.lower()  # should be "prompt"
        assert "reponse" not in AUDITOR_SYSTEM_PROMPT.lower()  # should be "response"
