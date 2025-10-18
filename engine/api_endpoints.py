"""
API Endpoints for Cognition Engine

Provides HTTP endpoints that wrap the Cognition Engine SDK functionality,
enabling external EdTech platforms to integrate via REST API calls.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from supabase import Client, create_client
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from .cognition_engine import CognitionEngine
from .api_auth import validate_api_key, track_api_usage

# Initialize Cognition Engine
cognition_engine = CognitionEngine(
    supabase_url=os.getenv("SUPABASE_URL", ""),
    supabase_key=os.getenv("SUPABASE_ANON_KEY", "")
)

router = APIRouter(prefix="/api/v1", tags=["cognition-api"])


# ===== PYDANTIC MODELS =====

class TrackAnswerRequest(BaseModel):
    """Request model for tracking learning events"""
    user_id: str = Field(..., description="Unique identifier for the student")
    skill_id: str = Field(..., description="Unique identifier for the skill/topic")
    is_correct: bool = Field(..., description="Whether the answer was correct")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on the question")
    confidence_score: Optional[int] = Field(None, description="Self-reported confidence 1-5")
    question_difficulty: Optional[float] = Field(None, description="Question difficulty -3 to +3")

class BatchTrackRequest(BaseModel):
    """Request model for batch processing multiple events"""
    events: List[Dict[str, Any]] = Field(..., description="List of learning events to process")


# ===== API ENDPOINTS =====

@router.post("/track-answer", status_code=status.HTTP_200_OK)
async def track_learning_event(
    request: TrackAnswerRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Track a learning event and update all relevant analytics.

    This is the primary endpoint for recording practice sessions and
    triggering all cognitive analytics updates.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        # Track the answer using Cognition Engine
        result = await cognition_engine.track_answer(
            user_id=request.user_id,
            skill_id=request.skill_id,
            is_correct=request.is_correct,
            time_spent_seconds=request.time_spent_seconds,
            confidence_score=request.confidence_score,
            question_difficulty=request.question_difficulty
        )

        # Track usage for billing
        await track_api_usage(api_key, "/track-answer", request.user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Learning event tracked successfully"
        }

    except Exception as e:
        # Track error for monitoring
        await track_api_usage(api_key, "/track-answer", request.user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track learning event: {str(e)}"
        )


@router.get("/predictions/{user_id}", status_code=status.HTTP_200_OK)
async def get_predictions(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Get comprehensive predictive analytics for a user.

    Returns predictions, goals, and personalized recommendations.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.get_predictions(user_id)

        # Track usage for billing
        await track_api_usage(api_key, "/predictions", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Predictions retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/predictions", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get predictions: {str(e)}"
        )


@router.get("/velocity/{user_id}", status_code=status.HTTP_200_OK)
async def get_learning_velocity(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Get comprehensive learning velocity and momentum analysis.

    Returns velocity metrics, trends, and momentum scores.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.get_learning_velocity(user_id)

        # Track usage for billing
        await track_api_usage(api_key, "/velocity", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Learning velocity retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/velocity", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning velocity: {str(e)}"
        )


@router.get("/cognitive-efficiency/{user_id}", status_code=status.HTTP_200_OK)
async def get_cognitive_efficiency(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Get cognitive efficiency metrics for a user.

    Returns efficiency metrics and learning effectiveness insights.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.get_cognitive_efficiency(user_id)

        # Track usage for billing
        await track_api_usage(api_key, "/cognitive-efficiency", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Cognitive efficiency retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/cognitive-efficiency", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cognitive efficiency: {str(e)}"
        )


@router.post("/batch-track", status_code=status.HTTP_200_OK)
async def batch_track_answers(
    request: BatchTrackRequest,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Efficiently process multiple learning events in batch.

    Useful for bulk importing historical data or high-frequency updates.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.batch_track_answers(request.events)

        # Track usage for billing (count events as requests)
        await track_api_usage(api_key, "/batch-track", user_id=None, db=db)

        return {
            "success": True,
            "data": result,
            "message": f"Batch processed {result['total_events']} events successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/batch-track", user_id=None, db=db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch process events: {str(e)}"
        )


@router.post("/performance-snapshot/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_performance_snapshot(
    user_id: str,
    snapshot_type: str = "manual",
    related_id: Optional[str] = None,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Create a comprehensive performance snapshot.

    Useful for capturing learning state at specific points in time.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.create_performance_snapshot(
            user_id=user_id,
            snapshot_type=snapshot_type,
            related_id=related_id
        )

        # Track usage for billing
        await track_api_usage(api_key, "/performance-snapshot", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Performance snapshot created successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/performance-snapshot", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create performance snapshot: {str(e)}"
        )


@router.get("/comprehensive-insights/{user_id}", status_code=status.HTTP_200_OK)
async def get_comprehensive_insights(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Get comprehensive learning insights combining all analytics.

    Returns all available insights and personalized recommendations.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.get_comprehensive_insights(user_id)

        # Track usage for billing
        await track_api_usage(api_key, "/comprehensive-insights", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Comprehensive insights retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/comprehensive-insights", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comprehensive insights: {str(e)}"
        )


# ===== VECTOR DATABASE ENDPOINTS (Optional) =====

@router.get("/similar-problems/{user_id}", status_code=status.HTTP_200_OK)
async def find_similar_problems(
    user_id: str,
    current_problem_id: str,
    limit: int = 5,
    difficulty_range: float = 1.0,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Find similar problems using semantic search.

    Requires vector database to be enabled.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.find_similar_problems(
            user_id=user_id,
            current_problem_id=current_problem_id,
            limit=limit,
            difficulty_range=difficulty_range
        )

        # Track usage for billing
        await track_api_usage(api_key, "/similar-problems", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Similar problems retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/similar-problems", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar problems: {str(e)}"
        )


@router.post("/analyze-code-similarity", status_code=status.HTTP_200_OK)
async def analyze_code_similarity(
    code_submission: str,
    reference_solutions: List[str],
    threshold: float = 0.8,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Analyze code similarity for plagiarism detection or pattern matching.

    Requires vector database to be enabled.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.analyze_code_similarity(
            code_submission=code_submission,
            reference_solutions=reference_solutions,
            threshold=threshold
        )

        # Track usage for billing
        await track_api_usage(api_key, "/analyze-code-similarity", user_id=None, db=db)

        return {
            "success": True,
            "data": result,
            "message": "Code similarity analysis completed"
        }

    except Exception as e:
        await track_api_usage(api_key, "/analyze-code-similarity", user_id=None, db=db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze code similarity: {str(e)}"
        )


@router.get("/similar-patterns/{user_id}", status_code=status.HTTP_200_OK)
async def find_similar_learning_patterns(
    user_id: str,
    limit: int = 10,
    api_key: str = Header(..., alias="X-API-Key"),
    db: Client = None
):
    """
    Find students with similar learning patterns and cognitive profiles.

    Requires vector database to be enabled.
    """
    # Validate API key
    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    key_info = await validate_api_key(api_key, db)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    try:
        result = await cognition_engine.find_similar_learning_patterns(
            user_id=user_id,
            limit=limit
        )

        # Track usage for billing
        await track_api_usage(api_key, "/similar-patterns", user_id, db)

        return {
            "success": True,
            "data": result,
            "message": "Similar learning patterns retrieved successfully"
        }

    except Exception as e:
        await track_api_usage(api_key, "/similar-patterns", user_id, db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar learning patterns: {str(e)}"
        )


# ===== UTILITY ENDPOINTS =====

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "cognition-engine-api",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/pricing", status_code=status.HTTP_200_OK)
async def get_pricing():
    """Get current pricing information"""
    return {
        "plans": {
            "starter": {
                "id": "price_starter",
                "name": "Starter",
                "price": 99,
                "currency": "USD",
                "interval": "month",
                "requests_per_month": 100000,
                "features": [
                    "Basic Analytics",
                    "Predictions",
                    "Velocity Tracking",
                    "Email Support"
                ]
            },
            "professional": {
                "id": "price_pro",
                "name": "Professional",
                "price": 299,
                "currency": "USD",
                "interval": "month",
                "requests_per_month": 1000000,
                "features": [
                    "All Analytics",
                    "Vector Search",
                    "Batch Processing",
                    "Priority Support",
                    "Custom Integrations"
                ]
            },
            "enterprise": {
                "id": "price_enterprise",
                "name": "Enterprise",
                "price": 999,
                "currency": "USD",
                "interval": "month",
                "requests_per_month": "Unlimited",
                "features": [
                    "All Features",
                    "Custom Models",
                    "Dedicated Support",
                    "SLA Guarantee",
                    "White-label Options"
                ]
            }
        }
    }
