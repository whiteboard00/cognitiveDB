"""
Cognition Engine SDK

A comprehensive learning analytics and prediction system that transforms
raw practice data into deep insights about student learning patterns.

This package provides:
- Bayesian Knowledge Tracing for skill mastery tracking
- Learning velocity and momentum analysis
- Predictive SAT scoring with confidence intervals
- Cognitive efficiency metrics
- Comprehensive performance snapshots

Main Classes:
- CognitionEngine: Main interface for all analytics operations
- BKTEngine: Specialized Bayesian Knowledge Tracing implementation
- VelocityEngine: Learning velocity and momentum calculations
- PredictionEngine: Predictive analytics for goal setting
- AnalyticsEngine: Performance snapshots and cognitive metrics
"""

from .cognition_engine import CognitionEngine, create_cognition_engine
from .bkt_engine import BKTEngine
from .velocity_engine import VelocityEngine
from .prediction_engine import PredictionEngine
from .analytics_engine import AnalyticsEngine

__version__ = "1.0.0"
__author__ = "Cognition Engine Team"

__all__ = [
    "CognitionEngine",
    "create_cognition_engine",
    "BKTEngine",
    "VelocityEngine",
    "PredictionEngine",
    "AnalyticsEngine"
]
