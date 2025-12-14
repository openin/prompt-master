from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analyzer import PromptAnalyzer

app = FastAPI(
    title="Prompt Master API",
    description="Audit LLM prompts against Google's 10 Golden Rules.",
    version="0.3.0",
)


# Pydantic Models
class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="The prompt text to audit")
    model: str = Field("gemini-2.0-flash", description="Gemini model version")


class Suggestion(BaseModel):
    rule: str
    advice: str


class AnalyzeResponse(BaseModel):
    score: int
    summary: str
    missing_rules: list[str] = []
    strengths: list[str] = []
    suggestions: list[Suggestion] = []


# Dependency
def get_analyzer(model: str = "gemini-2.0-flash"):
    try:
        return PromptAnalyzer(model_name=model)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "prompt-master"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(request: AnalyzeRequest):
    """
    Analyzes a prompt and returns a quality score and specific improvements.
    """
    analyzer = get_analyzer(request.model)
    result = await analyzer.analyze_async(request.prompt)
    return result
