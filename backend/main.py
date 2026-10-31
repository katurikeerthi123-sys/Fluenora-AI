import os
import sys
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.learning_engine import LearningEngine
from backend.academy.router import router as academy_router

# Global singleton engine
engine: Optional[LearningEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for initializing and tearing down application resources."""
    global engine
    try:
        engine = LearningEngine()
    except Exception as e:
        # Engine handles internal errors gracefully, but capture any unexpected initialization failure
        print(f"[Fluenora Startup] Error initializing LearningEngine: {e}", file=sys.stderr)
    yield
    # Shutdown logic if needed
    engine = None


app = FastAPI(
    title="Fluenora AI ✨ Backend API",
    description=(
        "Production-grade FastAPI service for Telugu-English grammar error classification, "
        "dedicated sentence correction, learning weakness analytics, and personalized practice."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend and external client integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(academy_router)


# ---------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------

class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        description="Learner sentence or answer to analyze for grammatical errors",
        examples=["Yesterday I am going to college."]
    )
    user_id: Optional[str] = Field(
        "default_user",
        description="User identifier for persistence and weakness tracking"
    )
    question_id: Optional[int] = Field(
        None,
        description="Optional practice question identifier being answered"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if v is None:
            raise ValueError("Input text cannot be None.")
        stripped = v.strip()
        if not stripped:
            raise ValueError("Input text cannot be empty or blank whitespace.")
        if len(stripped) > 1000:
            raise ValueError("Input text exceeds the maximum allowed length of 1,000 characters.")
        return stripped


class SubmissionRequest(BaseModel):
    text: str = Field(..., description="Answer text submitted by learner")
    question_id: int = Field(..., description="Question ID being answered")
    user_id: Optional[str] = Field("default_user", description="User identifier")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if v is None:
            raise ValueError("Input text cannot be None.")
        stripped = v.strip()
        if not stripped:
            raise ValueError("Input text cannot be empty or blank whitespace.")
        if len(stripped) > 1000:
            raise ValueError("Input text exceeds the maximum allowed length of 1,000 characters.")
        return stripped


def get_engine() -> LearningEngine:
    global engine
    if engine is None:
        engine = LearningEngine()
    return engine


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint reporting server status, model readiness, and version."""
    eng = get_engine()
    is_ready = eng.model_status == "ready"
    return {
        "status": "healthy" if is_ready else "degraded",
        "model_status": eng.model_status,
        "model_error": eng.model_error,
        "database": "connected",
        "version": "1.0.0"
    }


@app.post("/analyze", tags=["Inference & Analysis"])
@app.post("/api/analyze", tags=["Inference & Analysis"])
async def analyze_sentence(payload: AnalyzeRequest) -> Dict[str, Any]:
    """
    POST /analyze:
    Accepts a learner's answer or sentence and returns:
      - Grammar category classification (Bi-LSTM model)
      - Top-3 prediction distribution with confidence scores
      - Dedicated sentence correction and linguistic explanation (Sentence Corrector)
      - Clear architectural disclaimer
      - Learning persistence record (submission ID)
    """
    eng = get_engine()

    try:
        result = eng.analyze_sentence(
            text=payload.text,
            user_id=payload.user_id or "default_user",
            question_id=payload.question_id,
            persist=True
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model inference failed: {str(re)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during analysis: {str(e)}"
        )


@app.post("/api/submissions", tags=["Practice & Learning"])
async def submit_answer(payload: SubmissionRequest) -> Dict[str, Any]:
    """
    Submit an answer to a specific practice question.
    Analyzes the grammar, updates user weaknesses and daily streak, and returns feedback.
    """
    eng = get_engine()
    try:
        result = eng.analyze_sentence(
            text=payload.text,
            user_id=payload.user_id or "default_user",
            question_id=payload.question_id,
            persist=True
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/questions/daily", tags=["Practice & Learning"])
async def get_daily_questions(limit: int = Query(5, ge=1, le=10)) -> List[Dict[str, Any]]:
    """Fetch daily practice questions rotated by calendar day."""
    eng = get_engine()
    return eng.get_daily_questions(limit=limit)


@app.get("/api/questions/next", tags=["Practice & Learning"])
async def get_personalized_question(user_id: str = Query("default_user")) -> Dict[str, Any]:
    """
    Fetch a personalized next practice question specifically targeting
    the learner's highest-frequency grammar error category.
    """
    eng = get_engine()
    return eng.get_personalized_question(user_id=user_id)


@app.get("/api/user/{user_id}/progress", tags=["User Progress"])
async def get_user_progress(user_id: str) -> Dict[str, Any]:
    """
    Fetch detailed learning analytics for a user:
      - Overall submission count and accuracy percentage
      - Current daily active streak and total days active
      - Frequency breakdown of errors across all 7 grammar categories
      - Primary grammar weakness identified
      - Recent submission history with model feedback
    """
    eng = get_engine()
    return eng.get_user_progress(user_id=user_id)


@app.get("/api/metrics", tags=["Evaluation & Methodology"])
async def get_model_metrics() -> Dict[str, Any]:
    """
    Fetch verified experimental evaluation metrics and dataset methodology.
    Returns:
      - Test set accuracies (Bi-LSTM: 84.70%, MLP: 81.42%)
      - Parameter counts and precision/recall/F1 metrics from saved/model_comparison.json
      - Training epoch logs
      - Dataset methodology and synthetic limitation notes
    """
    eng = get_engine()
    return eng.get_model_metrics()


# ---------------------------------------------------------
# Static Assets & Frontend UI Hosting
# ---------------------------------------------------------

frontend_dir = os.path.join(PROJECT_ROOT, "frontend")
frontend_react_dist = os.path.join(PROJECT_ROOT, "frontend-react", "dist")
saved_dir = os.path.join(PROJECT_ROOT, "saved")

if os.path.exists(saved_dir):
    app.mount("/saved", StaticFiles(directory=saved_dir), name="saved")

if os.path.exists(frontend_react_dist):
    assets_dir = os.path.join(frontend_react_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="react_assets")

    @app.get("/academy", include_in_schema=False)
    async def serve_academy():
        index_file = os.path.join(frontend_react_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "Academy React frontend build not found."})

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse({"message": "Fluenora AI Backend is running. Frontend index.html not found."})
