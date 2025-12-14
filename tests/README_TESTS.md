# Tests for Prompt Master

This test suite provides comprehensive coverage for the `prompt_master` project.

## Test Structure

```
tests/
├── conftest.py              # pytest configuration and shared fixtures
├── pytest.ini              # pytest configuration
├── test_analyzer.py        # Unit tests for analyzer.py
├── test_api.py            # Unit tests for api.py
├── test_cli.py            # Unit tests for cli.py
├── test_system_prompts.py # Unit tests for system_prompts.py
├── test_integration.py    # End-to-end integration tests
└── README.md              # This file
```

## Installing Test Dependencies

```bash
uv pip install pytest pytest-cov pytest-asyncio httpx
```

## Running Tests

### All tests with coverage
```bash
uv run pytest --cov=src/prompt_master tests
```

### Tests with detailed report
```bash
uv run pytest --cov=src/prompt_master --cov-report=html tests
```

### Specific tests

#### Unit tests for a module
```bash
uv run pytest tests/test_analyzer.py -v
uv run pytest tests/test_api.py -v
uv run pytest tests/test_cli.py -v
```

#### Integration tests only
```bash
uv run pytest tests/test_integration.py -v
```

#### Tests by markers
```bash
# API tests only
uv run pytest -m api

# CLI tests only
uv run pytest -m cli

# Unit tests only
uv run pytest -m unit
```

### Useful Options

```bash
# Show print output
uv run pytest -s

# Stop at first failure
uv run pytest -x

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto

# Verbose mode with details
uv run pytest -vv

# Show slowest tests
uv run pytest --durations=10
```

## Code Coverage

Tests aim for a minimum coverage of 80%. The coverage report shows:

- **Lines covered**: Percentage of lines executed
- **Branches covered**: Percentage of conditional branches tested
- **Missing lines**: Lines not tested

### Generate HTML report
```bash
uv run pytest --cov=src/prompt_master --cov-report=html tests
# Open htmlcov/index.html in a browser
```

## Test Descriptions

### test_analyzer.py
- ✅ Initialization with/without API key
- ✅ Model configuration
- ✅ Synchronous and asynchronous analysis
- ✅ Error handling
- ✅ JSON parsing
- ✅ Error response generation

**Coverage**: ~95%

### test_api.py
- ✅ FastAPI endpoints (/health, /analyze)
- ✅ Request validation (Pydantic)
- ✅ Custom models
- ✅ HTTP error handling
- ✅ Structured JSON responses
- ✅ OpenAPI schema

**Coverage**: ~90%

### test_cli.py
- ✅ analyze command (text and file)
- ✅ serve command
- ✅ CLI options (--model, --json-output)
- ✅ Formatted output (rich)
- ✅ CLI error handling
- ✅ Help messages

**Coverage**: ~85%

### test_system_prompts.py
- ✅ System prompt existence
- ✅ Content of 10 golden rules
- ✅ JSON structure
- ✅ Required fields
- ✅ Prompt quality

**Coverage**: ~100%

### test_integration.py
- ✅ Complete API workflow
- ✅ Multiple scenarios (good/bad prompts)
- ✅ Production error handling
- ✅ Multiple requests
- ✅ Model selection
- ✅ Response structure

**Coverage**: End-to-end tests

## Important Fixtures

### conftest.py
- `test_prompt_examples`: Prompt examples (good, bad, perfect)
- `sample_api_response`: Typical response structure
- `mock_gemini_response`: Mock Gemini responses
- `temp_prompt_file`: Temporary file for CLI tests

## Mocking

Tests use `unittest.mock` for:
- **Gemini API**: Avoid real calls and costs
- **Files**: CLI tests without external dependencies
- **Uvicorn**: Test server without actual startup

## CI/CD

These tests are designed to integrate easily into a CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    uv pip install pytest pytest-cov pytest-asyncio
    uv run pytest --cov=src/prompt_master tests
```

## Contributing

To add tests:
1. Follow the `test_*.py` naming convention
2. Use existing fixtures
3. Add descriptive docstrings
4. Aim for >80% coverage for new code
5. Test both nominal and error cases

## Troubleshooting

### ImportError: No module named 'prompt_master'
```bash
# Ensure PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Async tests failing
```bash
# Verify pytest-asyncio is installed
uv pip install pytest-asyncio
```

### Coverage issues
```bash
# Clean .pyc files and __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Quality Metrics

Goals:
- ✅ Code coverage: ≥ 80%
- ✅ Branch coverage: ≥ 70%
- ✅ All tests passing: 100%
- ✅ Execution time: < 5 seconds

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Typer Testing](https://typer.tiangolo.com/tutorial/testing/)