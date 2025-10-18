#!/usr/bin/env python3
"""
Example usage of the Cognition Engine SDK

This script demonstrates how to integrate the Cognition Engine
into an educational platform for advanced learning analytics.
"""

import asyncio
import os
from datetime import datetime

# Import the Cognition Engine SDK
from cognition_engine import CognitionEngine, create_cognition_engine


async def main():
    """Demonstrate Cognition Engine capabilities"""

    # Initialize the engine
    # In production, use environment variables for credentials
    engine = create_cognition_engine(
        supabase_url="https://your-project.supabase.co",
        supabase_key="your-anon-key"
    )

    print("🤖 Cognition Engine SDK Demo")
    print("=" * 50)

    # Example 1: Track a learning event
    print("\n1. Tracking a learning event...")

    track_result = await engine.track_answer(
        user_id="student_123",
        skill_id="algebra_linear_equations",
        is_correct=True,
        time_spent_seconds=75,
        confidence_score=4,
        question_difficulty=0.5
    )

    if track_result["success"]:
        print(f"✅ Mastery updated: {track_result['mastery_before']".3f"} → {track_result['mastery_after']".3f"}")
        print(f"📈 Learning velocity: {track_result['velocity']".4f"}")
        print(f"🎯 Cognitive efficiency: {track_result.get('cognitive_efficiency', 'N/A')}")
    else:
        print(f"❌ Error: {track_result.get('error', 'Unknown error')}")

    # Example 2: Get predictive insights
    print("\n2. Getting predictive insights...")

    predictions = await engine.get_predictions("student_123")

    if "error" not in predictions:
        print(f"📊 Current total score: {predictions['current_total']}")
        print(f"🎯 Predicted in 30 days: {predictions['predicted_total_in_30_days']}")
        print(f"📅 Goal status: {predictions['goal_status']}")
        print(f"✅ On track: {predictions['on_track']}")

        if predictions["recommendations"]:
            print("💡 Recommendations:")
            for rec in predictions["recommendations"]:
                print(f"   • {rec}")
    else:
        print(f"❌ Error: {predictions.get('error', 'Unknown error')}")

    # Example 3: Analyze learning velocity
    print("\n3. Analyzing learning velocity...")

    velocity = await engine.get_learning_velocity("student_123")

    if "error" not in velocity:
        print(f"🚀 Overall velocity: {velocity['overall_velocity']} pts/week")
        print(f"💪 Momentum score: {velocity['momentum_score']}/100")
        print(f"📈 Improving: {velocity['is_improving']}")

        if velocity["velocity_by_skill"]:
            print("🔥 Top improving skills:")
            for skill in velocity["velocity_by_skill"][:3]:
                print(f"   • {skill['skill_name']}: {skill['velocity']".4f"} velocity")
    else:
        print(f"❌ Error: {velocity.get('error', 'Unknown error')}")

    # Example 4: Get cognitive efficiency
    print("\n4. Analyzing cognitive efficiency...")

    efficiency = await engine.get_cognitive_efficiency("student_123")

    if "error" not in efficiency:
        print(f"⏱️  Avg time per question: {efficiency.get('avg_time_per_question', 'N/A')}s")
        print(f"🎯 Avg confidence: {efficiency.get('avg_confidence_score', 'N/A')}/5")
        print(f"🧠 Cognitive efficiency: {efficiency.get('cognitive_efficiency_score', 'N/A')}")
        print(f"📊 Total questions: {efficiency.get('total_questions', 0)}")
    else:
        print(f"❌ Error: {efficiency.get('error', 'Unknown error')}")

    # Example 5: Create performance snapshot
    print("\n5. Creating performance snapshot...")

    snapshot = await engine.create_performance_snapshot(
        user_id="student_123",
        snapshot_type="demo_session"
    )

    if "error" not in snapshot:
        print(f"📸 Snapshot created: {snapshot.get('snapshot_type', 'unknown')}")
        print(f"🎯 Predicted Math: {snapshot.get('predicted_sat_math', 'N/A')}")
        print(f"🎯 Predicted R&W: {snapshot.get('predicted_sat_rw', 'N/A')}")
        print(f"📊 Questions answered: {snapshot.get('questions_answered', 0)}")
    else:
        print(f"❌ Error: {snapshot.get('error', 'Unknown error')}")

    # Example 6: Get comprehensive insights
    print("\n6. Getting comprehensive insights...")

    insights = await engine.get_comprehensive_insights("student_123")

    if "error" not in insights:
        print("🎭 Comprehensive Analysis:")
        print(f"   • Generated: {insights['generated_at']}")

        if "summary" in insights:
            summary = insights["summary"]
            for key, value in summary.items():
                print(f"   • {key.title()}: {value}")

        if "priority_recommendations" in insights:
            print("🚨 Priority Recommendations:")
            for rec in insights["priority_recommendations"]:
                print(f"   • {rec}")
    else:
        print(f"❌ Error: {insights.get('error', 'Unknown error')}")

    # Example 7: Batch processing
    print("\n7. Batch processing multiple events...")

    batch_events = [
        {
            "user_id": "student_456",
            "skill_id": "geometry_triangles",
            "is_correct": True,
            "time_spent_seconds": 60,
            "confidence_score": 3
        },
        {
            "user_id": "student_456",
            "skill_id": "geometry_triangles",
            "is_correct": False,
            "time_spent_seconds": 90,
            "confidence_score": 2
        },
        {
            "user_id": "student_789",
            "skill_id": "reading_comprehension",
            "is_correct": True,
            "time_spent_seconds": 45,
            "confidence_score": 5
        }
    ]

    batch_result = await engine.batch_track_answers(batch_events)

    print(f"📦 Batch processed: {batch_result['successful_events']}/{batch_result['total_events']} successful")
    if batch_result["errors"]:
        print(f"❌ {len(batch_result['errors'])} errors occurred")

    # Example 8: Health check
    print("\n8. System health check...")

    health = await engine.health_check()

    print(f"🏥 System status: {health['status']}")
    print(f"📊 Total requests: {health['performance']['total_requests']}")
    print(f"❌ Error rate: {health['performance']['error_rate_percent']}%")

    # Example 9: Usage statistics
    print("\n9. Usage statistics...")

    usage = await engine.get_usage_stats(timeframe_days=7)

    if "error" not in usage:
        print(f"📈 Last 7 days:")
        print(f"   • Learning events: {usage['total_learning_events']}")
        print(f"   • Unique users: {usage['unique_users']}")
        print(f"   • Engine requests: {usage['engine_requests']}")
    else:
        print(f"❌ Error: {usage.get('error', 'Unknown error')}")

    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("• Integrate the SDK into your learning platform")
    print("• Set up database tables using the provided migrations")
    print("• Configure authentication and user management")
    print("• Customize BKT parameters for your specific use case")
    print("• Implement real-time dashboards using the analytics data")


async def demo_error_handling():
    """Demonstrate error handling capabilities"""

    print("\n🛠️  Error Handling Demo")
    print("=" * 30)

    # Initialize with invalid credentials to show error handling
    engine = create_cognition_engine(
        supabase_url="https://invalid-url.supabase.co",
        supabase_key="invalid-key"
    )

    # This will demonstrate graceful error handling
    result = await engine.track_answer(
        user_id="test_user",
        skill_id="test_skill",
        is_correct=True
    )

    if not result["success"]:
        print(f"✅ Error handling works: {result['error']}")

    health = await engine.health_check()
    if health["status"] == "error":
        print(f"✅ Health check error handling: {health['error']}")


async def demo_vector_database():
    """Demonstrate vector database capabilities"""

    print("\n🧠 Vector Database Demo")
    print("=" * 40)

    # Initialize with vector database support
    import chromadb

    # Set up ChromaDB (in production, use persistent storage)
    chroma_client = chromadb.EphemeralClient()
    collection = chroma_client.create_collection(name="learning_content")

    engine = create_cognition_engine(
        supabase_url="https://your-project.supabase.co",
        supabase_key="your-anon-key",
        vector_db_client=chroma_client,
        vector_collection=collection
    )

    print("✅ Vector database initialized")

    # 1. Embed learning content
    print("\n1. Embedding learning content...")

    content_results = []
    sample_problems = [
        {
            "id": "algebra_001",
            "title": "Solving Linear Equations",
            "content": "Learn to solve equations of the form ax + b = c",
            "type": "lesson"
        },
        {
            "id": "geometry_001",
            "title": "Triangle Properties",
            "content": "Understanding angles, sides, and triangle theorems",
            "type": "lesson"
        }
    ]

    for problem in sample_problems:
        result = await engine.embed_content(
            content_id=problem["id"],
            content=problem["content"],
            content_type=problem["type"],
            metadata={"title": problem["title"]}
        )
        content_results.append(result)
        print(f"   📚 Embedded: {problem['title']}")

    # 2. Semantic search
    print("\n2. Semantic content search...")

    search_result = await engine.search_content(
        query="how to solve equations",
        content_type="lesson",
        limit=3
    )

    if "error" not in search_result:
        print(f"🔍 Search query: '{search_result['query']}'")
        print(f"📊 Found {search_result['results_found']} results:")
        for result in search_result["search_results"]:
            print(f"   • {result['similarity_score']".3f"} - {result['metadata'].get('title', 'Unknown')}")
    else:
        print(f"❌ Search error: {search_result['error']}")

    # 3. Similar problem recommendations
    print("\n3. Similar problem recommendations...")

    similar_result = await engine.find_similar_problems(
        user_id="student_123",
        current_problem_id="algebra_001",
        limit=3
    )

    if "error" not in similar_result:
        print(f"🎯 Current problem: {similar_result['current_problem']}")
        print(f"🔗 Similar problems found: {similar_result['total_found']}")
        for problem in similar_result["similar_problems"]:
            print(f"   • {problem['similarity_score']".3f"} - {problem['title']}")
    else:
        print(f"❌ Similar problems error: {similar_result['error']}")

    # 4. Code similarity analysis
    print("\n4. Code similarity analysis...")

    user_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

    reference_solutions = [
        """
def two_sum_optimized(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""",
        """
def two_sum_brute_force(numbers, target):
    for x in range(len(numbers)):
        for y in range(x + 1, len(numbers)):
            if numbers[x] + numbers[y] == target:
                return [x, y]
    return []
"""
    ]

    similarity_result = await engine.analyze_code_similarity(
        code_submission=user_code,
        reference_solutions=reference_solutions,
        threshold=0.7
    )

    if "error" not in similarity_result:
        print(f"🔍 Max similarity: {similarity_result['max_similarity']".3f"}")
        print(f"⚠️ Risk level: {similarity_result['risk_level']}")
        print(f"💡 Recommendation: {similarity_result['recommendation']}")
    else:
        print(f"❌ Similarity analysis error: {similarity_result['error']}")

    # 5. Learning pattern matching
    print("\n5. Learning pattern matching...")

    pattern_result = await engine.find_similar_learning_patterns(
        user_id="student_123",
        limit=3
    )

    if "error" not in pattern_result:
        print(f"👥 Found {pattern_result['total_similar_found']} students with similar patterns")
        for student in pattern_result["similar_students"]:
            print(f"   • User {student['user_id']}: {student['similarity_score']".3f"} similarity")
    else:
        print(f"❌ Pattern matching error: {pattern_result['error']}")


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(main())

    # Run vector database demo
    print("\n" + "="*60)
    asyncio.run(demo_vector_database())

    # Optionally run error handling demo
    # asyncio.run(demo_error_handling())
