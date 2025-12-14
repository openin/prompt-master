FROM python:3.13-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_PYTHON_VERSION_CHECK=on
RUN pip install uv
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-editable

EXPOSE 8000
CMD [".venv/bin/uvicorn", "prompt_master.api:app", "--host", "0.0.0.0", "--port", "8000"]