"""
Bayesian Knowledge Tracing (BKT) Engine

Advanced implementation of Bayesian Knowledge Tracing for skill mastery tracking.
This module provides the core BKT algorithms used by the Cognition Engine.
"""

from typing import Dict, Optional, Any
from datetime import datetime
from supabase import Client


class BKTEngine:
    """
    Bayesian Knowledge Tracing Engine

    Implements the four-parameter BKT model:
    - P(L0): Prior knowledge probability
    - P(T): Learning rate (transition probability)
    - P(G): Guess probability (correct without mastery)
    - P(S): Slip probability (incorrect despite mastery)
    """

    def __init__(self, db: Client):
        """
        Initialize the BKT Engine.

        Args:
            db: Supabase client instance
        """
        self.db = db

        # Default BKT parameters (can be customized per skill)
        self.default_parameters = {
            "prior_knowledge": 0.25,      # P(L0) - initial mastery probability
            "learn_rate": 0.10,           # P(T) - learning rate per question
            "guess_probability": 0.25,    # P(G) - lucky guess probability
            "slip_probability": 0.10      # P(S) - careless error probability
        }

    async def update_mastery(
        self,
        user_id: str,
        skill_id: str,
        is_correct: bool,
        time_spent_seconds: Optional[int] = None,
        confidence_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update student mastery probability using Bayesian Knowledge Tracing.

        Args:
            user_id: Unique student identifier
            skill_id: Unique skill/topic identifier
            is_correct: Whether the answer was correct
            time_spent_seconds: Time spent on question (optional)
            confidence_score: Self-reported confidence 1-5 (optional)

        Returns:
            Dictionary with updated mastery information
        """
        # Get or create mastery record
        mastery_record = await self._get_or_create_mastery_record(user_id, skill_id)

        # Extract current parameters
        current_mastery = float(mastery_record["mastery_probability"])
        p_learn = float(mastery_record["learn_rate"])
        p_guess = float(mastery_record["guess_probability"])
        p_slip = float(mastery_record["slip_probability"])

        # Bayesian update based on evidence
        posterior_mastery = self._bayesian_update(
            prior_mastery=current_mastery,
            is_correct=is_correct,
            p_guess=p_guess,
            p_slip=p_slip
        )

        # Apply learning transition
        new_mastery = self._apply_learning_transition(
            posterior=posterior_mastery,
            p_learn=p_learn
        )

        # Update record in database
        update_result = await self._update_mastery_record(
            mastery_id=mastery_record["id"],
            new_mastery=new_mastery,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            confidence_score=confidence_score
        )

        # Calculate learning velocity
        velocity = new_mastery - current_mastery

        # Detect plateau conditions
        plateau_detected = self._detect_plateau(
            total_attempts=update_result["total_attempts"],
            velocity=velocity
        )

        # Log learning event
        await self._log_learning_event(
            user_id=user_id,
            skill_id=skill_id,
            event_type="mastery_updated",
            mastery_before=current_mastery,
            mastery_after=new_mastery,
            event_data={
                "is_correct": is_correct,
                "velocity": round(velocity, 4),
                "time_spent_seconds": time_spent_seconds,
                "confidence_score": confidence_score,
                "plateau_detected": plateau_detected
            }
        )

        return {
            "skill_id": skill_id,
            "mastery_before": round(current_mastery, 4),
            "mastery_after": round(new_mastery, 4),
            "velocity": round(velocity, 4),
            "total_attempts": update_result["total_attempts"],
            "correct_attempts": update_result["correct_attempts"],
            "plateau_detected": plateau_detected,
            "timestamp": datetime.now().isoformat()
        }

    def _bayesian_update(
        self,
        prior_mastery: float,
        is_correct: bool,
        p_guess: float,
        p_slip: float
    ) -> float:
        """
        Apply Bayesian update based on answer correctness.

        Args:
            prior_mastery: Prior mastery probability
            is_correct: Whether answer was correct
            p_guess: Guess probability
            p_slip: Slip probability

        Returns:
            Posterior mastery probability
        """
        if is_correct:
            # P(L|correct) = P(L) * (1 - P(S)) / [P(L) * (1 - P(S)) + (1 - P(L)) * P(G)]
            numerator = prior_mastery * (1 - p_slip)
            denominator = numerator + (1 - prior_mastery) * p_guess
        else:
            # P(L|incorrect) = P(L) * P(S) / [P(L) * P(S) + (1 - P(L)) * (1 - P(G))]
            numerator = prior_mastery * p_slip
            denominator = numerator + (1 - prior_mastery) * (1 - p_guess)

        if denominator == 0:
            return prior_mastery

        posterior = numerator / denominator

        # Clamp to reasonable bounds
        return max(0.01, min(0.99, posterior))

    def _apply_learning_transition(self, posterior: float, p_learn: float) -> float:
        """
        Apply learning transition probability.

        Args:
            posterior: Posterior mastery after evidence
            p_learn: Learning rate parameter

        Returns:
            New mastery probability after learning opportunity
        """
        # P(L_new) = P(L|evidence) + (1 - P(L|evidence)) * P(T)
        new_mastery = posterior + (1 - posterior) * p_learn

        # Clamp to reasonable bounds
        return max(0.01, min(0.99, new_mastery))

    async def _get_or_create_mastery_record(self, user_id: str, skill_id: str) -> Dict[str, Any]:
        """Get existing mastery record or create new one."""
        # Try to get existing record
        result = self.db.table("user_skill_mastery").select("*").eq(
            "user_id", user_id
        ).eq("skill_id", skill_id).execute()

        if result.data:
            return result.data[0]

        # Create new record with default parameters
        return await self._create_mastery_record(user_id, skill_id)

    async def _create_mastery_record(self, user_id: str, skill_id: str) -> Dict[str, Any]:
        """Create a new mastery record with default parameters."""
        insert_data = {
            "user_id": user_id,
            "skill_id": skill_id,
            **self.default_parameters,
            "total_attempts": 0,
            "correct_attempts": 0,
            "plateau_flag": False,
            "created_at": datetime.now().isoformat()
        }

        result = self.db.table("user_skill_mastery").insert(insert_data).execute()

        if not result.data:
            raise Exception("Failed to create mastery record")

        return result.data[0]

    async def _update_mastery_record(
        self,
        mastery_id: str,
        new_mastery: float,
        is_correct: bool,
        time_spent_seconds: Optional[int] = None,
        confidence_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update mastery record in database."""
        # Get current record for incrementing counters
        current_result = self.db.table("user_skill_mastery").select(
            "total_attempts, correct_attempts"
        ).eq("id", mastery_id).execute()

        if not current_result.data:
            raise Exception("Mastery record not found")

        current = current_result.data[0]
        total_attempts = current["total_attempts"] + 1
        correct_attempts = current["correct_attempts"] + (1 if is_correct else 0)

        # Calculate learning velocity
        velocity = new_mastery - float(current.get("mastery_probability", 0.25))

        update_data = {
            "mastery_probability": round(new_mastery, 4),
            "learning_velocity": round(velocity, 4),
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "last_practiced_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Update record
        self.db.table("user_skill_mastery").update(update_data).eq("id", mastery_id).execute()

        return {
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts
        }

    def _detect_plateau(
        self,
        total_attempts: int,
        velocity: float,
        threshold_attempts: int = 10,
        velocity_threshold: float = 0.02
    ) -> bool:
        """
        Detect if student has reached a learning plateau.

        Args:
            total_attempts: Total number of attempts for this skill
            velocity: Current learning velocity
            threshold_attempts: Minimum attempts before plateau detection
            velocity_threshold: Velocity threshold for plateau detection

        Returns:
            True if plateau detected
        """
        if total_attempts < threshold_attempts:
            return False

        # Plateau if velocity is very small (less than 2% change)
        return abs(velocity) < velocity_threshold

    async def _log_learning_event(
        self,
        user_id: str,
        skill_id: str,
        event_type: str,
        mastery_before: float,
        mastery_after: float,
        event_data: Dict[str, Any]
    ):
        """Log a learning event to the database."""
        try:
            self.db.table("learning_events").insert({
                "user_id": user_id,
                "skill_id": skill_id,
                "event_type": event_type,
                "mastery_before": round(mastery_before, 4),
                "mastery_after": round(mastery_after, 4),
                "event_data": event_data,
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to log learning event: {e}")
            # Don't fail the main operation for logging errors

    async def get_mastery_probability(self, user_id: str, skill_id: str) -> Optional[float]:
        """
        Get current mastery probability for a user-skill pair.

        Args:
            user_id: Unique student identifier
            skill_id: Unique skill identifier

        Returns:
            Current mastery probability (0.0-1.0) or None if not found
        """
        result = self.db.table("user_skill_mastery").select("mastery_probability").eq(
            "user_id", user_id
        ).eq("skill_id", skill_id).execute()

        if result.data:
            return float(result.data[0]["mastery_probability"])

        return None

    async def get_user_skill_masteries(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all skill masteries for a user.

        Args:
            user_id: Unique student identifier

        Returns:
            List of mastery records with skill details
        """
        result = self.db.table("user_skill_mastery").select(
            "*, topics(id, name, category_id, categories(id, name, section))"
        ).eq("user_id", user_id).execute()

        return result.data if result.data else []

    async def reset_skill_mastery(self, user_id: str, skill_id: str) -> bool:
        """
        Reset mastery tracking for a specific skill (admin function).

        Args:
            user_id: Unique student identifier
            skill_id: Unique skill identifier

        Returns:
            True if reset successful
        """
        try:
            # Delete existing mastery record
            self.db.table("user_skill_mastery").delete().eq(
                "user_id", user_id
            ).eq("skill_id", skill_id).execute()

            # Log reset event
            await self._log_learning_event(
                user_id=user_id,
                skill_id=skill_id,
                event_type="mastery_reset",
                mastery_before=0.0,
                mastery_after=self.default_parameters["prior_knowledge"],
                event_data={"reason": "admin_reset"}
            )

            return True

        except Exception as e:
            print(f"Error resetting skill mastery: {e}")
            return False

    def customize_parameters(
        self,
        skill_id: str,
        prior_knowledge: Optional[float] = None,
        learn_rate: Optional[float] = None,
        guess_probability: Optional[float] = None,
        slip_probability: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Customize BKT parameters for a specific skill.

        Args:
            skill_id: Unique skill identifier
            prior_knowledge: Initial mastery probability (0.0-1.0)
            learn_rate: Learning rate per question (0.0-1.0)
            guess_probability: Guess probability (0.0-1.0)
            slip_probability: Slip probability (0.0-1.0)

        Returns:
            Dictionary of customized parameters
        """
        customized = self.default_parameters.copy()

        if prior_knowledge is not None:
            customized["prior_knowledge"] = max(0.01, min(0.99, prior_knowledge))
        if learn_rate is not None:
            customized["learn_rate"] = max(0.01, min(0.99, learn_rate))
        if guess_probability is not None:
            customized["guess_probability"] = max(0.01, min(0.99, guess_probability))
        if slip_probability is not None:
            customized["slip_probability"] = max(0.01, min(0.99, slip_probability))

        return customized

    async def get_skill_statistics(self, skill_id: str) -> Dict[str, Any]:
        """
        Get aggregate statistics for a skill across all users.

        Args:
            skill_id: Unique skill identifier

        Returns:
            Dictionary containing skill statistics
        """
        try:
            result = self.db.table("user_skill_mastery").select(
                "mastery_probability, total_attempts, correct_attempts, learning_velocity"
            ).eq("skill_id", skill_id).execute()

            if not result.data:
                return {
                    "total_users": 0,
                    "avg_mastery": 0.0,
                    "avg_attempts": 0.0,
                    "avg_accuracy": 0.0,
                    "avg_velocity": 0.0
                }

            data = result.data
            total_users = len(data)
            avg_mastery = sum(float(record["mastery_probability"]) for record in data) / total_users
            avg_attempts = sum(record["total_attempts"] for record in data) / total_users
            avg_accuracy = sum(
                record["correct_attempts"] / record["total_attempts"]
                for record in data
                if record["total_attempts"] > 0
            ) / total_users
            avg_velocity = sum(float(record["learning_velocity"]) for record in data) / total_users

            return {
                "total_users": total_users,
                "avg_mastery": round(avg_mastery, 3),
                "avg_attempts": round(avg_attempts, 1),
                "avg_accuracy": round(avg_accuracy, 3),
                "avg_velocity": round(avg_velocity, 4),
                "skill_id": skill_id
            }

        except Exception as e:
            print(f"Error getting skill statistics: {e}")
            return {
                "error": str(e),
                "skill_id": skill_id
            }
