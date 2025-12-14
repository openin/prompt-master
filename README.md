# Prompt Master 🧠✨

**Prompt Master** is a robust Python tool designed to audit and optimize your prompts for Large Language Models (LLMs) like Gemini, GPT-4, and Claude.

It leverages the power of **Gemini Flash** models for **semantic analysis**, checking your prompts against the **10 Golden Rules of Prompting** derived from official Google AI documentation.

## 🏆 Project Status

| Metric | Status |
| :--- | :--- |
| **Pipeline Status** | [![CI Pipeline Status](https://github.com/openin/prompt-master/actions/workflows/ci.yml/badge.svg)](https://github.com/openin/prompt-master/actions/workflows/ci.yml) |
| **Latest Release** | [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/openin/prompt-master?sort=semver)](https://github.com/openin/prompt-master/releases/latest) |
| **Test Coverage** | [![Coverage Status](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/openin/prompt-master/actions/workflows/ci.yml) |
| **License** | [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) |

## 🌟 Features

* **AI-Powered Analysis**: Uses `gemini-2.0-flash` for high-speed, semantic auditing, moving beyond simple keyword checks.
* **CLI Interface**: Quick and easy prompt analysis directly from your terminal.
* **REST API (FastAPI)**: Deployable as a microservice for seamless integration into larger applications. 
* **High Code Quality**: Enforced use of `black`, `ruff`, and `pytest`.
* **Dockerized**: Simple, portable deployment of the FastAPI service.

## 📜 The 10 Golden Rules

The tool validates your prompt structure against these key principles, ensuring maximum performance for "Deep Thinking" LLMs:

1.  **Clarity**: Directness and zero ambiguity.
2.  **Persona**: Specific role assignment (e.g., "Act as a lawyer").
3.  **Format/Tone**: Explicit output structure (JSON, List, Table) and required tone.
4.  **Priority**: Constraints and persona placed *before* the main task.
5.  **Context**: Sufficient background data is provided.
6.  **Action Verbs**: Use of strong, specific directives (e.g., "Analyze", "Code").
7.  **Anchoring**: Transition phrases linking instructions to context (e.g., "Based on the text above...").
8.  **Length Control**: Explicit constraints on verbosity.
9.  **Iteration**: Encourages refinement.
10. **Fact Checking**: Reminder/check for citation requests on sensitive topics.

---

## 🚀 Installation & Usage

### Prerequisites

1.  **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Install `uv`**: `pip install uv`

### Local Setup

1.  **Clone & Sync**:
    ```bash
    git clone [https://github.com/openin/prompt-master.git](https://github.com/openin/prompt-master.git)
    cd prompt-master
    # Installs default and 'dev' dependencies (including FastAPI, pytest, black, ruff)
    uv sync --all-extras 
    ```

2.  **Set Environment Variable**:
    ```bash
    export GEMINI_API_KEY="YOUR_KEY_HERE"
    ```

### CLI Usage

Use the `prompt-master` command via `uv run`:

| Command | Description |
| :--- | :--- |
| `uv run prompt-master analyze "Your prompt here"` | Analyze a string prompt. |
| `uv run prompt-master analyze file.txt` | Analyze a prompt from a file. |
| `uv run prompt-master serve` | Start the FastAPI server (default: `http://127.0.0.1:8000`). |

---

## 🐳 Docker Deployment

To run the Prompt Master API as a containerized microservice:

1.  **Build the Image**:
    ```bash
    docker build -t prompt-master-api .
    ```

2.  **Run the Container**:
    Pass the `GEMINI_API_KEY` as an environment variable when running.
    ```bash
    docker run -d \
      --name prompt_master \
      -p 8000:8000 \
      -e GEMINI_API_KEY="YOUR_KEY_HERE" \
      prompt-master-api
    ```
    The API will be available at `http://localhost:8000`.

---

## 🧑‍💻 Development and Quality

The project enforces high code quality using a strict CI pipeline.

### Tools

* **`black`**: Code formatter.
* **`ruff`**: Extremely fast Python linter and formatter.
* **`pytest`**: Testing framework.

### Quality Checks

Before submitting a Pull Request, please ensure the following commands pass:

1.  **Formatting Check**:
    ```bash
    uv run black --check src tests
    ```
2.  **Linting Check**:
    ```bash
    uv run ruff check src tests
    ```
3.  **Run Tests and Coverage**:
    ```bash
    # Run tests using the mocked Gemini response
    uv run pytest 
    ```

### GitHub Actions Pipeline

Our CI pipeline (`.github/workflows/ci.yml`) automatically runs the checks above for every push, ensuring the stability and quality of the `main` branch.

## 📄 License

This project is licensed under the **MIT License**.