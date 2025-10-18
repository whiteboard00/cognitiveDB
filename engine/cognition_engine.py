"""
Cognition Engine SDK - Main Interface

This module provides the main CognitionEngine class that serves as the primary
interface for all learning analytics and prediction capabilities.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from supabase import Client, create_client

from .bkt_engine import BKTEngine
from .velocity_engine import VelocityEngine
from .prediction_engine import PredictionEngine
from .analytics_engine import AnalyticsEngine


class CognitionEngine:
    """
    Main interface for the Cognition Engine SDK.

    Provides unified access to all learning analytics capabilities:
    - Bayesian Knowledge Tracing (BKT)
    - Learning Velocity & Momentum Analysis
    - Predictive Scoring & Goal Tracking
    - Cognitive Efficiency Metrics
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        database_url: Optional[str] = None,
        vector_db_client: Optional[Any] = None,
        vector_collection: Optional[Any] = None
    ):
        """
        Initialize the Cognition Engine.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon/public key
            database_url: Optional direct database URL for advanced usage
            vector_db_client: Optional vector database client (e.g., ChromaDB)
            vector_collection: Optional vector collection for semantic search
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.database_url = database_url

        # Initialize Supabase client
        self.db: Client = create_client(supabase_url, supabase_key)

        # Initialize component engines
        self.bkt_engine = BKTEngine(self.db)
        self.velocity_engine = VelocityEngine(self.db)
        self.prediction_engine = PredictionEngine(self.db)
        self.analytics_engine = AnalyticsEngine(self.db)

        # Vector database support (optional)
        self.vector_db_client = vector_db_client
        self.vector_collection = vector_collection
        self.vector_enabled = vector_db_client is not None and vector_collection is not None

        # Performance tracking
        self.request_count = 0
        self.error_count = 0

    async def track_answer(
        self,
        user_id: str,
        skill_id: str,
        is_correct: bool,
        time_spent_seconds: Optional[int] = None,
        confidence_score: Optional[int] = None,
        question_difficulty: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Track a learning event and update all relevant analytics.

        This is the primary method for recording practice sessions and
        triggering all cognitive analytics updates.

        Args:
            user_id: Unique identifier for the student
            skill_id: Unique identifier for the skill/topic
            is_correct: Whether the answer was correct
            time_spent_seconds: Time spent on the question (optional)
            confidence_score: Self-reported confidence 1-5 (optional)
            question_difficulty: Question difficulty -3 to +3 (optional)

        Returns:
            Dictionary containing updated mastery, velocity, and insights
        """
        self.request_count += 1

        try:
            # Update BKT mastery
            bkt_result = await self.bkt_engine.update_mastery(
                user_id=user_id,
                skill_id=skill_id,
                is_correct=is_correct,
                time_spent_seconds=time_spent_seconds,
                confidence_score=confidence_score
            )

            # Calculate cognitive efficiency if we have required data
            efficiency_score = None
            if time_spent_seconds and confidence_score:
                efficiency_score = self.analytics_engine.calculate_cognitive_efficiency(
                    time_spent_seconds=time_spent_seconds,
                    confidence_score=confidence_score,
                    is_correct=is_correct,
                    difficulty=question_difficulty or 0.0
                )

            # Log comprehensive learning event
            await self._log_comprehensive_event(
                user_id=user_id,
                skill_id=skill_id,
                event_type="question_answered",
                bkt_data=bkt_result,
                cognitive_data={
                    "efficiency_score": efficiency_score,
                    "time_spent_seconds": time_spent_seconds,
                    "confidence_score": confidence_score,
                    "question_difficulty": question_difficulty
                }
            )

            return {
                "success": True,
                "mastery_before": bkt_result["mastery_before"],
                "mastery_after": bkt_result["mastery_after"],
                "velocity": bkt_result["velocity"],
                "total_attempts": bkt_result["total_attempts"],
                "correct_attempts": bkt_result["correct_attempts"],
                "plateau_detected": bkt_result.get("plateau_detected", False),
                "cognitive_efficiency": efficiency_score,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error tracking answer: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_predictions(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive predictive analytics for a user.

        Args:
            user_id: Unique identifier for the student

        Returns:
            Dictionary containing predictions, goals, and recommendations
        """
        self.request_count += 1

        try:
            return await self.prediction_engine.calculate_predictive_scores(user_id)
        except Exception as e:
            self.error_count += 1
            print(f"Error getting predictions: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_learning_velocity(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning velocity and momentum analysis.

        Args:
            user_id: Unique identifier for the student

        Returns:
            Dictionary containing velocity metrics and trends
        """
        self.request_count += 1

        try:
            return await self.velocity_engine.calculate_learning_velocity(user_id)
        except Exception as e:
            self.error_count += 1
            print(f"Error getting learning velocity: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_cognitive_efficiency(self, user_id: str) -> Dict[str, Any]:
        """
        Get cognitive efficiency metrics for a user.

        Args:
            user_id: Unique identifier for the student

        Returns:
            Dictionary containing efficiency metrics and insights
        """
        self.request_count += 1

        try:
            # Get recent practice data
            recent_data = await self.analytics_engine._get_recent_practice_data(user_id)

            if not recent_data:
                return {
                    "avg_time_per_question": None,
                    "avg_confidence_score": None,
                    "cognitive_efficiency_score": None,
                    "total_questions": 0,
                    "message": "No recent practice data available"
                }

            # Calculate efficiency metrics
            times = [q.get("time_spent_seconds", 0) for q in recent_data if q.get("time_spent_seconds")]
            confidences = [q.get("confidence_score", 0) for q in recent_data if q.get("confidence_score")]

            avg_time = sum(times) / len(times) if times else None
            avg_confidence = sum(confidences) / len(confidences) if confidences else None

            # Calculate overall efficiency
            efficiency_scores = []
            for question in recent_data:
                if (question.get("time_spent_seconds") and
                    question.get("confidence_score") and
                    question.get("user_answer") is not None):

                    is_correct = self._check_answer_correctness(
                        question["user_answer"],
                        question["correct_answer"]
                    )

                    efficiency = self.analytics_engine.calculate_cognitive_efficiency(
                        time_spent_seconds=question["time_spent_seconds"],
                        confidence_score=question["confidence_score"],
                        is_correct=is_correct,
                        difficulty=question.get("difficulty", 0.0)
                    )
                    efficiency_scores.append(efficiency)

            overall_efficiency = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else None

            return {
                "avg_time_per_question": round(avg_time, 2) if avg_time else None,
                "avg_confidence_score": round(avg_confidence, 2) if avg_confidence else None,
                "cognitive_efficiency_score": round(overall_efficiency, 3) if overall_efficiency else None,
                "total_questions": len(recent_data),
                "efficiency_trend": "improving" if overall_efficiency and overall_efficiency > 0.7 else "needs_work",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error getting cognitive efficiency: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def create_performance_snapshot(
        self,
        user_id: str,
        snapshot_type: str = "manual",
        related_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive performance snapshot.

        Args:
            user_id: Unique identifier for the student
            snapshot_type: Type of snapshot ('manual', 'session_complete', 'weekly', etc.)
            related_id: Optional related session or exam ID

        Returns:
            Dictionary containing the created snapshot data
        """
        self.request_count += 1

        try:
            return await self.analytics_engine.create_performance_snapshot(
                user_id=user_id,
                snapshot_type=snapshot_type,
                related_id=related_id
            )
        except Exception as e:
            self.error_count += 1
            print(f"Error creating performance snapshot: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_comprehensive_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning insights combining all analytics.

        Args:
            user_id: Unique identifier for the student

        Returns:
            Dictionary containing all available insights and recommendations
        """
        self.request_count += 1

        try:
            # Gather all insights in parallel for better performance
            predictions_task = self.get_predictions(user_id)
            velocity_task = self.get_learning_velocity(user_id)
            efficiency_task = self.get_cognitive_efficiency(user_id)
            snapshot_task = self.create_performance_snapshot(user_id, "comprehensive")

            predictions, velocity, efficiency, snapshot = await asyncio.gather(
                predictions_task, velocity_task, efficiency_task, snapshot_task
            )

            # Combine insights
            return {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "predictions": predictions,
                "learning_velocity": velocity,
                "cognitive_efficiency": efficiency,
                "current_snapshot": snapshot,
                "summary": self._generate_insights_summary(predictions, velocity, efficiency),
                "priority_recommendations": self._generate_priority_recommendations(
                    predictions, velocity, efficiency
                )
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error getting comprehensive insights: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def batch_track_answers(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Efficiently process multiple learning events in batch.

        Args:
            events: List of learning event dictionaries

        Returns:
            Dictionary containing batch processing results
        """
        self.request_count += 1

        results = []
        errors = []

        for event in events:
            try:
                result = await self.track_answer(**event)
                results.append(result)
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "event": event,
                    "timestamp": datetime.now().isoformat()
                }
                errors.append(error_result)

        return {
            "total_events": len(events),
            "successful_events": len(results),
            "failed_events": len(errors),
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the Cognition Engine.

        Returns:
            Dictionary containing health status and metrics
        """
        try:
            # Test database connectivity
            db_health = await self._check_database_health()

            # Calculate performance metrics
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0

            return {
                "status": "healthy" if db_health["status"] == "connected" else "unhealthy",
                "database": db_health,
                "performance": {
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "error_rate_percent": round(error_rate, 2),
                    "uptime": "unknown"  # Would need to track start time
                },
                "components": {
                    "bkt_engine": "operational",
                    "velocity_engine": "operational",
                    "prediction_engine": "operational",
                    "analytics_engine": "operational"
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and basic operations."""
        try:
            # Simple query to test connection
            result = self.db.table("users").select("count", count="exact").limit(1).execute()
            return {
                "status": "connected",
                "response_time_ms": "unknown"  # Would need to measure
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _check_answer_correctness(self, user_answer: Any, correct_answer: Any) -> bool:
        """Check if user's answer matches correct answer."""
        if user_answer is None or correct_answer is None:
            return False

        # Handle list answers (multiple choice, multiple select)
        if isinstance(user_answer, list) and isinstance(correct_answer, list):
            return sorted(user_answer) == sorted(correct_answer)

        # Handle single answers
        return user_answer == correct_answer

    async def _log_comprehensive_event(
        self,
        user_id: str,
        skill_id: str,
        event_type: str,
        bkt_data: Dict[str, Any],
        cognitive_data: Dict[str, Any]
    ):
        """Log a comprehensive learning event with all available data."""
        try:
            self.db.table("learning_events").insert({
                "user_id": user_id,
                "skill_id": skill_id,
                "event_type": event_type,
                "mastery_before": bkt_data.get("mastery_before"),
                "mastery_after": bkt_data.get("mastery_after"),
                "event_data": {
                    "velocity": bkt_data.get("velocity"),
                    "total_attempts": bkt_data.get("total_attempts"),
                    "cognitive_efficiency": cognitive_data.get("efficiency_score"),
                    "time_spent_seconds": cognitive_data.get("time_spent_seconds"),
                    "confidence_score": cognitive_data.get("confidence_score"),
                    "question_difficulty": cognitive_data.get("question_difficulty")
                }
            }).execute()
        except Exception as e:
            print(f"Error logging comprehensive event: {e}")
            # Don't fail the main operation for logging errors

    def _generate_insights_summary(
        self,
        predictions: Dict[str, Any],
        velocity: Dict[str, Any],
        efficiency: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a human-readable summary of insights."""
        summary = {}

        # Prediction summary
        if "current_total" in predictions:
            summary["prediction"] = (
                f"Currently at {predictions['current_total']} total SAT score, "
                f"predicted to reach {predictions.get('predicted_total_in_30_days', 'N/A')} in 30 days"
            )

        # Velocity summary
        if "momentum_score" in velocity:
            momentum = velocity["momentum_score"]
            if momentum >= 80:
                summary["momentum"] = f"Excellent momentum ({momentum}/100) - learning at optimal pace"
            elif momentum >= 60:
                summary["momentum"] = f"Good momentum ({momentum}/100) - consistent progress"
            elif momentum >= 40:
                summary["momentum"] = f"Moderate momentum ({momentum}/100) - room for improvement"
            else:
                summary["momentum"] = f"Low momentum ({momentum}/100) - needs increased practice"

        # Efficiency summary
        if "cognitive_efficiency_score" in efficiency and efficiency["cognitive_efficiency_score"]:
            efficiency_score = efficiency["cognitive_efficiency_score"]
            if efficiency_score >= 0.8:
                summary["efficiency"] = f"High cognitive efficiency ({efficiency_score".3f"}) - learning very effectively"
            elif efficiency_score >= 0.6:
                summary["efficiency"] = f"Good cognitive efficiency ({efficiency_score".3f"}) - learning well"
            else:
                summary["efficiency"] = f"Low cognitive efficiency ({efficiency_score".3f"}) - may need strategy adjustments"

        return summary

    def _generate_priority_recommendations(
        self,
        predictions: Dict[str, Any],
        velocity: Dict[str, Any],
        efficiency: Dict[str, Any]
    ) -> List[str]:
        """Generate prioritized recommendations based on all insights."""
        recommendations = []

        # High priority: Goal tracking issues
        if predictions.get("on_track") is False:
            recommendations.append("🚨 PRIORITY: You're behind your study goals. Consider increasing practice time.")

        # Medium priority: Momentum issues
        if velocity.get("momentum_score", 100) < 60:
            recommendations.append("📈 Improve learning momentum with more consistent daily practice.")

        # Medium priority: Efficiency issues
        if efficiency.get("cognitive_efficiency_score", 1.0) and efficiency["cognitive_efficiency_score"] < 0.6:
            recommendations.append("🧠 Focus on active learning strategies to improve cognitive efficiency.")

        # Low priority: Plateau detection
        if velocity.get("velocity_by_skill"):
            plateaued_skills = [
                skill for skill in velocity["velocity_by_skill"]
                if skill.get("category") == "Plateau"
            ]
            if plateaued_skills:
                skill_names = [skill["skill_name"] for skill in plateaued_skills[:3]]
                recommendations.append(f"🔄 Consider new approaches for: {', '.join(skill_names)}")

        # Always include positive reinforcement if doing well
        if (predictions.get("on_track") is True and
            velocity.get("momentum_score", 0) >= 70 and
            efficiency.get("cognitive_efficiency_score", 0) >= 0.7):
            recommendations.append("✅ Excellent progress! Keep up the great work.")

        return recommendations[:3]  # Limit to top 3 recommendations

    async def get_usage_stats(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for the engine.

        Args:
            timeframe_days: Number of days to analyze

        Returns:
            Dictionary containing usage metrics
        """
        cutoff_date = datetime.now().timestamp() - (timeframe_days * 24 * 60 * 60)

        try:
            # Get learning events count
            events_result = self.db.table("learning_events").select(
                "count", count="exact"
            ).gte("created_at", datetime.fromtimestamp(cutoff_date).isoformat()).execute()

            # Get unique users
            users_result = self.db.table("learning_events").select(
                "user_id", count="exact", distinct=True
            ).gte("created_at", datetime.fromtimestamp(cutoff_date).isoformat()).execute()

            return {
                "timeframe_days": timeframe_days,
                "total_learning_events": events_result.count,
                "unique_users": users_result.count,
                "engine_requests": self.request_count,
                "engine_errors": self.error_count,
                "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # ===== VECTOR DATABASE METHODS (Optional) =====

    async def find_similar_problems(
        self,
        user_id: str,
        current_problem_id: str,
        limit: int = 5,
        difficulty_range: float = 1.0
    ) -> Dict[str, Any]:
        """
        Find similar problems using semantic search.

        Args:
            user_id: Student ID for personalized recommendations
            current_problem_id: Current problem to find similar ones for
            limit: Maximum number of similar problems to return
            difficulty_range: Difficulty tolerance (± this value)

        Returns:
            Dictionary containing similar problems with relevance scores
        """
        if not self.vector_enabled:
            return {
                "error": "Vector database not enabled",
                "similar_problems": [],
                "message": "Enable vector database for semantic search"
            }

        self.request_count += 1

        try:
            # Get current problem details
            current_problem = await self._get_problem_details(current_problem_id)
            if not current_problem:
                return {"error": "Current problem not found", "similar_problems": []}

            # Generate embedding for current problem
            current_embedding = await self._generate_problem_embedding(current_problem)

            # Search for similar problems
            similar_results = self.vector_collection.query(
                query_embeddings=[current_embedding],
                n_results=limit * 2,  # Get more to filter by difficulty
                where={"type": "problem"}
            )

            # Filter and rank by difficulty preference
            similar_problems = []
            current_difficulty = current_problem.get("difficulty", 0)

            for result in similar_results["metadatas"][0]:
                problem_difficulty = result.get("difficulty", 0)
                difficulty_diff = abs(problem_difficulty - current_difficulty)

                if difficulty_diff <= difficulty_range:
                    similar_problems.append({
                        "problem_id": result["problem_id"],
                        "title": result["title"],
                        "similarity_score": result["score"],
                        "difficulty": problem_difficulty,
                        "difficulty_match": 1.0 - (difficulty_diff / difficulty_range),
                        "category": result.get("category", "unknown")
                    })

            # Sort by combined similarity and difficulty match
            similar_problems.sort(
                key=lambda x: (x["similarity_score"] * 0.7 + x["difficulty_match"] * 0.3),
                reverse=True
            )

            return {
                "current_problem": current_problem["title"],
                "similar_problems": similar_problems[:limit],
                "total_found": len(similar_problems),
                "vector_search_enabled": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error finding similar problems: {e}")
            return {
                "error": str(e),
                "similar_problems": [],
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_code_similarity(
        self,
        code_submission: str,
        reference_solutions: List[str],
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Analyze code similarity for plagiarism detection or pattern matching.

        Args:
            code_submission: User's submitted code
            reference_solutions: List of known solutions to compare against
            threshold: Similarity threshold for flagging (0.0-1.0)

        Returns:
            Dictionary containing similarity analysis results
        """
        if not self.vector_enabled:
            return {
                "error": "Vector database not enabled",
                "similarity_analysis": [],
                "message": "Enable vector database for code similarity analysis"
            }

        self.request_count += 1

        try:
            # Generate embedding for submitted code
            submission_embedding = await self._generate_code_embedding(code_submission)

            # Generate embeddings for reference solutions
            reference_embeddings = []
            for i, ref_code in enumerate(reference_solutions):
                ref_embedding = await self._generate_code_embedding(ref_code)
                reference_embeddings.append({
                    "index": i,
                    "embedding": ref_embedding,
                    "code": ref_code
                })

            # Calculate similarities
            similarities = []
            for ref in reference_embeddings:
                # Calculate cosine similarity (simplified)
                similarity = self._calculate_embedding_similarity(
                    submission_embedding,
                    ref["embedding"]
                )

                similarities.append({
                    "reference_index": ref["index"],
                    "similarity_score": similarity,
                    "is_similar": similarity >= threshold,
                    "reference_code_preview": ref["code"][:100] + "..." if len(ref["code"]) > 100 else ref["code"]
                })

            # Sort by similarity score
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

            # Determine overall assessment
            max_similarity = similarities[0]["similarity_score"] if similarities else 0.0
            risk_level = "high" if max_similarity >= 0.9 else "medium" if max_similarity >= 0.7 else "low"

            return {
                "submission_preview": code_submission[:100] + "..." if len(code_submission) > 100 else code_submission,
                "max_similarity": max_similarity,
                "risk_level": risk_level,
                "similarity_threshold": threshold,
                "reference_solutions_analyzed": len(reference_solutions),
                "similarities": similarities,
                "recommendation": self._generate_similarity_recommendation(max_similarity, threshold),
                "vector_search_enabled": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error analyzing code similarity: {e}")
            return {
                "error": str(e),
                "similarity_analysis": [],
                "timestamp": datetime.now().isoformat()
            }

    async def find_similar_learning_patterns(
        self,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Find students with similar learning patterns and cognitive profiles.

        Args:
            user_id: Student ID to find similar patterns for
            limit: Maximum number of similar students to return

        Returns:
            Dictionary containing students with similar learning patterns
        """
        if not self.vector_enabled:
            return {
                "error": "Vector database not enabled",
                "similar_students": [],
                "message": "Enable vector database for pattern matching"
            }

        self.request_count += 1

        try:
            # Get user's learning pattern vector
            user_pattern = await self._generate_learning_pattern_vector(user_id)
            if not user_pattern:
                return {"error": "No learning data available for user", "similar_students": []}

            # Search for similar patterns
            similar_results = self.vector_collection.query(
                query_embeddings=[user_pattern],
                n_results=limit + 1,  # +1 to exclude self
                where={"type": "learning_pattern"}
            )

            similar_students = []
            for result in similar_results["metadatas"][0]:
                if result["user_id"] != user_id:  # Exclude self
                    similar_students.append({
                        "user_id": result["user_id"],
                        "similarity_score": result["score"],
                        "pattern_type": result.get("pattern_type", "unknown"),
                        "avg_mastery": result.get("avg_mastery", 0),
                        "learning_velocity": result.get("learning_velocity", 0),
                        "cognitive_efficiency": result.get("cognitive_efficiency", 0)
                    })

            # Sort by similarity
            similar_students.sort(key=lambda x: x["similarity_score"], reverse=True)

            return {
                "target_user": user_id,
                "similar_students": similar_students[:limit],
                "total_similar_found": len(similar_students),
                "pattern_analysis": self._analyze_pattern_clusters(similar_students),
                "vector_search_enabled": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error finding similar learning patterns: {e}")
            return {
                "error": str(e),
                "similar_students": [],
                "timestamp": datetime.now().isoformat()
            }

    async def embed_content(
        self,
        content_id: str,
        content: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and store embeddings for learning content.

        Args:
            content_id: Unique identifier for the content
            content: Text content to embed
            content_type: Type of content ('problem', 'solution', 'explanation', etc.)
            metadata: Additional metadata for the content

        Returns:
            Dictionary containing embedding results
        """
        if not self.vector_enabled:
            return {
                "error": "Vector database not enabled",
                "embedding_stored": False,
                "message": "Enable vector database for content embedding"
            }

        self.request_count += 1

        try:
            # Generate embedding for content
            embedding = await self._generate_text_embedding(content)

            # Prepare metadata
            full_metadata = {
                "content_id": content_id,
                "type": content_type,
                "content_length": len(content),
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }

            # Store in vector database
            self.vector_collection.add(
                embeddings=[embedding],
                metadatas=[full_metadata],
                ids=[content_id]
            )

            return {
                "content_id": content_id,
                "content_type": content_type,
                "embedding_stored": True,
                "embedding_dimensions": len(embedding),
                "metadata": full_metadata,
                "vector_search_enabled": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error embedding content: {e}")
            return {
                "error": str(e),
                "embedding_stored": False,
                "timestamp": datetime.now().isoformat()
            }

    async def search_content(
        self,
        query: str,
        content_type: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Search learning content using semantic similarity.

        Args:
            query: Search query text
            content_type: Filter by content type (optional)
            limit: Maximum results to return
            threshold: Minimum similarity threshold

        Returns:
            Dictionary containing search results
        """
        if not self.vector_enabled:
            return {
                "error": "Vector database not enabled",
                "search_results": [],
                "message": "Enable vector database for semantic search"
            }

        self.request_count += 1

        try:
            # Generate embedding for query
            query_embedding = await self._generate_text_embedding(query)

            # Prepare search filter
            where_clause = {"type": content_type} if content_type else None

            # Search vector database
            search_results = self.vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # Get more to filter by threshold
                where=where_clause
            )

            # Filter by threshold and format results
            filtered_results = []
            for metadata, distance in zip(
                search_results["metadatas"][0],
                search_results["distances"][0]
            ):
                similarity = 1.0 - distance  # Convert distance to similarity

                if similarity >= threshold:
                    filtered_results.append({
                        "content_id": metadata["content_id"],
                        "content_type": metadata["type"],
                        "similarity_score": round(similarity, 3),
                        "metadata": metadata,
                        "relevance": self._calculate_relevance_score(similarity, metadata)
                    })

            # Sort by relevance
            filtered_results.sort(key=lambda x: x["relevance"], reverse=True)

            return {
                "query": query,
                "content_type_filter": content_type,
                "results_found": len(filtered_results),
                "similarity_threshold": threshold,
                "search_results": filtered_results[:limit],
                "vector_search_enabled": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.error_count += 1
            print(f"Error searching content: {e}")
            return {
                "error": str(e),
                "search_results": [],
                "timestamp": datetime.now().isoformat()
            }

    # ===== VECTOR DATABASE HELPER METHODS =====

    async def _generate_problem_embedding(self, problem: Dict[str, Any]) -> List[float]:
        """Generate embedding for a problem (title + description + tags)."""
        # This would use OpenAI embeddings or similar service
        # For now, return a placeholder
        import hashlib
        problem_text = f"{problem.get('title', '')} {problem.get('description', '')} {problem.get('tags', '')}"
        # Simple hash-based embedding (replace with real embedding service)
        hash_obj = hashlib.md5(problem_text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        # Generate pseudo-random but deterministic embedding
        embedding = [(hash_int >> (i * 4)) % 1000 / 1000.0 for i in range(384)]
        return embedding

    async def _generate_code_embedding(self, code: str) -> List[float]:
        """Generate embedding for code (AST-based or semantic)."""
        # This would use CodeBERT or similar code embedding model
        # For now, return a placeholder
        import hashlib
        # Normalize code (remove whitespace, comments)
        normalized_code = self._normalize_code(code)
        hash_obj = hashlib.md5(normalized_code.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        # Generate pseudo-random but deterministic embedding
        embedding = [(hash_int >> (i * 4)) % 1000 / 1000.0 for i in range(384)]
        return embedding

    async def _generate_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for general text content."""
        # This would use OpenAI text-embedding-ada-002 or similar
        # For now, return a placeholder
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        # Generate pseudo-random but deterministic embedding
        embedding = [(hash_int >> (i * 4)) % 1000 / 1000.0 for i in range(384)]
        return embedding

    async def _generate_learning_pattern_vector(self, user_id: str) -> Optional[List[float]]:
        """Generate vector representation of a user's learning pattern."""
        try:
            # Get user's mastery data
            mastery_data = await self.bkt_engine.get_user_skill_masteries(user_id)
            if not mastery_data:
                return None

            # Get user's velocity data
            velocity_data = await self.velocity_engine.calculate_learning_velocity(user_id)

            # Create pattern vector from multiple features
            pattern_features = []

            # Mastery probabilities
            masteries = [float(record["mastery_probability"]) for record in mastery_data]
            pattern_features.extend(masteries[:10])  # Limit to first 10 skills

            # Velocity metrics
            pattern_features.append(velocity_data.get("overall_velocity", 0))
            pattern_features.append(velocity_data.get("momentum_score", 50) / 100.0)
            pattern_features.append(velocity_data.get("acceleration", 1.0))

            # Pad or truncate to fixed size
            while len(pattern_features) < 50:
                pattern_features.append(0.0)

            return pattern_features[:50]

        except Exception as e:
            print(f"Error generating learning pattern vector: {e}")
            return None

    def _calculate_embedding_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            import math

            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))

            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in embedding1))
            magnitude2 = math.sqrt(sum(b * b for b in embedding2))

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            # Cosine similarity
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def _normalize_code(self, code: str) -> str:
        """Normalize code for consistent embedding generation."""
        import re

        # Remove comments (simple implementation)
        lines = code.split('\n')
        normalized_lines = []

        for line in lines:
            # Remove simple comments (language-specific logic would be better)
            if '//' in line:
                line = line.split('//')[0]
            elif '#' in line:
                line = line.split('#')[0]
            elif '/*' in line and '*/' in line:
                # Simple block comment removal
                line = re.sub(r'/\*.*?\*/', '', line)

            normalized_lines.append(line.strip())

        # Join and remove extra whitespace
        normalized = '\n'.join(normalized_lines)
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized.strip()

    def _generate_similarity_recommendation(self, max_similarity: float, threshold: float) -> str:
        """Generate recommendation based on similarity analysis."""
        if max_similarity >= 0.95:
            return "🚨 High similarity detected - potential plagiarism"
        elif max_similarity >= threshold:
            return "⚠️ Moderate similarity - review for learning patterns"
        else:
            return "✅ Low similarity - original work pattern"

    def _analyze_pattern_clusters(self, similar_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze clusters in similar learning patterns."""
        if not similar_students:
            return {"clusters": 0, "analysis": "No similar patterns found"}

        # Simple clustering based on pattern types
        pattern_types = {}
        for student in similar_students:
            pattern_type = student.get("pattern_type", "unknown")
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1

        return {
            "clusters": len(pattern_types),
            "dominant_pattern": max(pattern_types.items(), key=lambda x: x[1])[0] if pattern_types else "none",
            "pattern_distribution": pattern_types,
            "analysis": f"Found {len(pattern_types)} distinct learning pattern types"
        }

    def _calculate_relevance_score(self, similarity: float, metadata: Dict[str, Any]) -> float:
        """Calculate relevance score combining similarity and metadata factors."""
        base_score = similarity

        # Boost score for recent content
        created_at = metadata.get("created_at")
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_date).days
                recency_boost = max(0, 1.0 - (days_old / 365))  # Boost for content < 1 year old
                base_score *= (1.0 + recency_boost * 0.1)
            except:
                pass

        # Boost score for highly-rated or popular content
        rating = metadata.get("rating", 0)
        if rating > 0:
            rating_boost = rating / 5.0  # Assuming 5-star rating system
            base_score *= (1.0 + rating_boost * 0.05)

        return round(base_score, 3)

    async def _get_problem_details(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get problem details from database (placeholder implementation)."""
        # This would query your problems table
        # For now, return a placeholder
        return {
            "problem_id": problem_id,
            "title": f"Problem {problem_id}",
            "description": f"Description for {problem_id}",
            "difficulty": 0.5,
            "category": "algorithms",
            "tags": ["array", "hash-table"]
        }


# Convenience function for easy initialization
def create_cognition_engine(
    supabase_url: str,
    supabase_key: str,
    database_url: Optional[str] = None
) -> CognitionEngine:
    """
    Convenience function to create a CognitionEngine instance.

    Args:
        supabase_url: Supabase project URL
        supabase_key: Supabase anon/public key
        database_url: Optional direct database URL

    Returns:
        Configured CognitionEngine instance
    """
    return CognitionEngine(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        database_url=database_url
    )
