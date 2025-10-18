"""
Integration Examples for Cognition Engine API

Provides ready-to-use code examples for different programming languages
and frameworks that EdTech companies can copy and integrate.
"""

import asyncio
from typing import Dict, List, Optional
import requests
import json


class CognitionEngineAPI:
    """
    Python client for Cognition Engine API

    Example usage:
        client = CognitionEngineAPI(
            base_url="https://api.cognition-engine.com",
            api_key="your-api-key"
        )

        # Track learning event
        result = await client.track_answer(
            user_id="student_123",
            skill_id="algebra",
            is_correct=True
        )
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def track_answer(
        self,
        user_id: str,
        skill_id: str,
        is_correct: bool,
        time_spent_seconds: Optional[int] = None,
        confidence_score: Optional[int] = None,
        question_difficulty: Optional[float] = None
    ) -> Dict:
        """Track a learning event"""
        payload = {
            "user_id": user_id,
            "skill_id": skill_id,
            "is_correct": is_correct,
            "time_spent_seconds": time_spent_seconds,
            "confidence_score": confidence_score,
            "question_difficulty": question_difficulty
        }

        response = requests.post(
            f"{self.base_url}/api/v1/track-answer",
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")

    def get_predictions(self, user_id: str) -> Dict:
        """Get predictive analytics for a user"""
        response = requests.get(
            f"{self.base_url}/api/v1/predictions/{user_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")

    def get_learning_velocity(self, user_id: str) -> Dict:
        """Get learning velocity metrics"""
        response = requests.get(
            f"{self.base_url}/api/v1/velocity/{user_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")

    def batch_track_answers(self, events: List[Dict]) -> Dict:
        """Batch process multiple learning events"""
        payload = {"events": events}

        response = requests.post(
            f"{self.base_url}/api/v1/batch-track",
            headers=self.headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")


# ===== JAVASCRIPT/NODE.JS EXAMPLE =====

JAVASCRIPT_EXAMPLE = '''
// JavaScript/Node.js integration example
const COGNITION_API_URL = "https://api.cognition-engine.com";
const API_KEY = "your-api-key-here";

class CognitionEngineClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = "https://api.cognition-engine.com";
    }

    async trackAnswer(userId, skillId, isCorrect, options = {}) {
        const payload = {
            user_id: userId,
            skill_id: skillId,
            is_correct: isCorrect,
            time_spent_seconds: options.timeSpent,
            confidence_score: options.confidence,
            question_difficulty: options.difficulty
        };

        const response = await fetch(`${this.baseURL}/api/v1/track-answer`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": this.apiKey
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    }

    async getPredictions(userId) {
        const response = await fetch(
            `${this.baseURL}/api/v1/predictions/${userId}`,
            {
                headers: {
                    "X-API-Key": this.apiKey
                }
            }
        );

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    }
}

// Usage example
const client = new CognitionEngineClient(API_KEY);

// Track learning event
client.trackAnswer("student_123", "algebra", true, {
    timeSpent: 75,
    confidence: 4
}).then(result => {
    console.log("Mastery:", result.data.mastery_after);
});

// Get predictions
client.getPredictions("student_123").then(predictions => {
    console.log("Predicted score:", predictions.data.predicted_total_in_30_days);
});
'''


# ===== PHP EXAMPLE =====

PHP_EXAMPLE = '''
<?php
// PHP integration example
class CognitionEngineAPI {
    private $apiKey;
    private $baseUrl;

    public function __construct($apiKey, $baseUrl = "https://api.cognition-engine.com") {
        $this->apiKey = $apiKey;
        $this->baseUrl = rtrim($baseUrl, "/");
    }

    public function trackAnswer($userId, $skillId, $isCorrect, $options = []) {
        $payload = [
            "user_id" => $userId,
            "skill_id" => $skillId,
            "is_correct" => $isCorrect,
            "time_spent_seconds" => $options["time_spent"] ?? null,
            "confidence_score" => $options["confidence"] ?? null,
            "question_difficulty" => $options["difficulty"] ?? null
        ];

        return $this->makeRequest("POST", "/api/v1/track-answer", $payload);
    }

    public function getPredictions($userId) {
        return $this->makeRequest("GET", "/api/v1/predictions/" . $userId);
    }

    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->baseUrl . $endpoint;

        $headers = [
            "X-API-Key: " . $this->apiKey,
            "Content-Type: application/json"
        ];

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

        if ($method === "POST" && $data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("API Error: " . $response);
        }

        return json_decode($response, true);
    }
}

// Usage example
$client = new CognitionEngineAPI("your-api-key");

// Track learning event
$result = $client->trackAnswer("student_123", "algebra", true, [
    "time_spent" => 75,
    "confidence" => 4
]);

echo "Mastery: " . $result["data"]["mastery_after"];

// Get predictions
$predictions = $client->getPredictions("student_123");
echo "Predicted: " . $predictions["data"]["predicted_total_in_30_days"];
?>
'''


# ===== REACT HOOK EXAMPLE =====

REACT_HOOK_EXAMPLE = '''
// React hook for Cognition Engine integration
import { useState, useCallback } from "react";

const COGNITION_API_URL = "https://api.cognition-engine.com";
const API_KEY = process.env.REACT_APP_COGNITION_API_KEY;

export function useCognitionEngine() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const trackAnswer = useCallback(async (userId, skillId, isCorrect, options = {}) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${COGNITION_API_URL}/api/v1/track-answer`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": API_KEY
                },
                body: JSON.stringify({
                    user_id: userId,
                    skill_id: skillId,
                    is_correct: isCorrect,
                    time_spent_seconds: options.timeSpent,
                    confidence_score: options.confidence,
                    question_difficulty: options.difficulty
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const result = await response.json();
            return result.data;

        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const getPredictions = useCallback(async (userId) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `${COGNITION_API_URL}/api/v1/predictions/${userId}`,
                {
                    headers: {
                        "X-API-Key": API_KEY
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const result = await response.json();
            return result.data;

        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        trackAnswer,
        getPredictions,
        loading,
        error
    };
}

// Usage in React component
function LearningComponent({ userId, currentSkill }) {
    const { trackAnswer, getPredictions, loading } = useCognitionEngine();
    const [predictions, setPredictions] = useState(null);

    const handleAnswerSubmit = async (isCorrect, timeSpent, confidence) => {
        try {
            await trackAnswer(userId, currentSkill, isCorrect, {
                timeSpent,
                confidence
            });

            // Get updated predictions
            const newPredictions = await getPredictions(userId);
            setPredictions(newPredictions);

        } catch (error) {
            console.error("Failed to track answer:", error);
        }
    };

    return (
        <div>
            {predictions && (
                <div className="predictions">
                    <h3>Predicted Score: {predictions.predicted_total_in_30_days}</h3>
                    <p>Goal Status: {predictions.goal_status}</p>
                </div>
            )}

            <button
                onClick={() => handleAnswerSubmit(true, 75, 4)}
                disabled={loading}
            >
                Submit Correct Answer
            </button>
        </div>
    );
}
'''


# ===== DJANGO INTEGRATION EXAMPLE =====

DJANGO_EXAMPLE = '''
# Django integration example
# Add to your Django project

# settings.py
COGNITION_ENGINE = {
    "API_URL": "https://api.cognition-engine.com",
    "API_KEY": "your-api-key-here"
}

# models.py or views.py
import requests
import os
from django.conf import settings

class CognitionEngineService:
    def __init__(self):
        self.api_url = settings.COGNITION_ENGINE["API_URL"]
        self.api_key = settings.COGNITION_ENGINE["API_KEY"]
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def track_student_answer(self, student_id, skill_name, is_correct, **kwargs):
        """Track student learning event"""

        payload = {
            "user_id": f"student_{student_id}",
            "skill_id": skill_name,
            "is_correct": is_correct,
            "time_spent_seconds": kwargs.get("time_spent"),
            "confidence_score": kwargs.get("confidence"),
            "question_difficulty": kwargs.get("difficulty")
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/track-answer",
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return result["data"]
            else:
                print(f"Cognition API Error: {response.text}")
                return None

        except Exception as e:
            print(f"Failed to track answer: {e}")
            return None

    def get_student_predictions(self, student_id):
        """Get predictions for student"""

        try:
            response = requests.get(
                f"{self.api_url}/api/v1/predictions/student_{student_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                result = response.json()
                return result["data"]
            else:
                print(f"Cognition API Error: {response.text}")
                return None

        except Exception as e:
            print(f"Failed to get predictions: {e}")
            return None

# Usage in Django view
def submit_answer(request, question_id):
    if request.method == "POST":
        # Your existing answer processing logic
        is_correct = validate_answer(request.POST.get("answer"))

        # Track with Cognition Engine
        cognition = CognitionEngineService()
        cognitive_result = cognition.track_student_answer(
            student_id=request.user.id,
            skill_name=get_skill_for_question(question_id),
            is_correct=is_correct,
            time_spent=request.POST.get("time_spent"),
            confidence=request.POST.get("confidence")
        )

        # Get updated predictions
        predictions = cognition.get_student_predictions(request.user.id)

        return render(request, "question_result.html", {
            "is_correct": is_correct,
            "predictions": predictions
        })
'''


# ===== LARAVEL/PHP EXAMPLE =====

LARAVEL_EXAMPLE = '''
<?php
// Laravel service for Cognition Engine integration
namespace App\\Services;

use Illuminate\\Support\\Facades\\Http;
use Illuminate\\Support\\Facades\\Log;

class CognitionEngineService
{
    private $apiUrl;
    private $apiKey;

    public function __construct()
    {
        $this->apiUrl = config("cognition.api_url", "https://api.cognition-engine.com");
        $this->apiKey = config("cognition.api_key");
    }

    public function trackAnswer($userId, $skillId, $isCorrect, $options = [])
    {
        try {
            $response = Http::withHeaders([
                "X-API-Key" => $this->apiKey,
                "Content-Type" => "application/json"
            ])->post("{$this->apiUrl}/api/v1/track-answer", [
                "user_id" => $userId,
                "skill_id" => $skillId,
                "is_correct" => $isCorrect,
                "time_spent_seconds" => $options["time_spent"] ?? null,
                "confidence_score" => $options["confidence"] ?? null,
                "question_difficulty" => $options["difficulty"] ?? null
            ]);

            if ($response->successful()) {
                return $response->json()["data"];
            } else {
                Log::error("Cognition API Error", [
                    "status" => $response->status(),
                    "body" => $response->body()
                ]);
                return null;
            }

        } catch (\\Exception $e) {
            Log::error("Failed to track answer", ["error" => $e->getMessage()]);
            return null;
        }
    }

    public function getPredictions($userId)
    {
        try {
            $response = Http::withHeaders([
                "X-API-Key" => $this->apiKey
            ])->get("{$this->apiUrl}/api/v1/predictions/{$userId}");

            if ($response->successful()) {
                return $response->json()["data"];
            } else {
                Log::error("Cognition API Error", [
                    "status" => $response->status(),
                    "body" => $response->body()
                ]);
                return null;
            }

        } catch (\\Exception $e) {
            Log::error("Failed to get predictions", ["error" => $e->getMessage()]);
            return null;
        }
    }
}

// Usage in Laravel controller
public function submitAnswer(Request $request)
{
    $isCorrect = $this->validateAnswer($request->input("answer"));

    $cognition = new CognitionEngineService();
    $cognitiveResult = $cognition->trackAnswer(
        $request->user()->id,
        $request->input("skill_name"),
        $isCorrect,
        [
            "time_spent" => $request->input("time_spent"),
            "confidence" => $request->input("confidence")
        ]
    );

    $predictions = $cognition->getPredictions($request->user()->id);

    return response()->json([
        "is_correct" => $isCorrect,
        "predictions" => $predictions
    ]);
}
?>
'''


# ===== .NET/C# EXAMPLE =====

CSHARP_EXAMPLE = '''
// C#/.NET integration example
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class CognitionEngineClient
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public CognitionEngineClient(string apiKey, string baseUrl = "https://api.cognition-engine.com")
    {
        _apiKey = apiKey;
        _baseUrl = baseUrl.TrimEnd('/');
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
    }

    public async Task<TrackAnswerResponse> TrackAnswerAsync(
        string userId,
        string skillId,
        bool isCorrect,
        int? timeSpentSeconds = null,
        int? confidenceScore = null,
        double? questionDifficulty = null)
    {
        var payload = new
        {
            user_id = userId,
            skill_id = skillId,
            is_correct = isCorrect,
            time_spent_seconds = timeSpentSeconds,
            confidence_score = confidenceScore,
            question_difficulty = questionDifficulty
        };

        var json = JsonConvert.SerializeObject(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/track-answer", content);

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"API Error: {response.StatusCode}");
        }

        var responseJson = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<TrackAnswerResponse>(responseJson);
    }

    public async Task<PredictionsResponse> GetPredictionsAsync(string userId)
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/api/v1/predictions/{userId}");

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"API Error: {response.StatusCode}");
        }

        var responseJson = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<PredictionsResponse>(responseJson);
    }
}

// Usage in ASP.NET Core
public class LearningController : Controller
{
    private readonly CognitionEngineClient _cognitionClient;

    public LearningController()
    {
        _cognitionClient = new CognitionEngineClient(
            Configuration["CognitionEngine:ApiKey"]
        );
    }

    [HttpPost]
    public async Task<IActionResult> SubmitAnswer([FromBody] SubmitAnswerRequest request)
    {
        try {
            var result = await _cognitionClient.TrackAnswerAsync(
                User.Identity.Name,
                request.SkillId,
                request.IsCorrect,
                request.TimeSpentSeconds,
                request.ConfidenceScore
            );

            var predictions = await _cognitionClient.GetPredictionsAsync(User.Identity.Name);

            return Ok(new {
                is_correct = request.IsCorrect,
                predictions = predictions.Data
            });
        }
        catch (Exception ex) {
            return StatusCode(500, new { error = ex.Message });
        }
    }
}
'''


def print_integration_examples():
    """Print all integration examples"""

    examples = {
        "Python": f"""
# Python Integration Example
from cognition_engine import CognitionEngine

client = CognitionEngine(
    base_url="https://api.cognition-engine.com",
    api_key="your-api-key"
)

# Track learning event
result = await client.track_answer(
    user_id="student_123",
    skill_id="algebra_linear",
    is_correct=True,
    time_spent_seconds=75,
    confidence_score=4
)

# Get predictions
predictions = await client.get_predictions("student_123")
print(f"Predicted score: {predictions['predicted_total_in_30_days']}")
""",

        "JavaScript": f"""
{JAVASCRIPT_EXAMPLE}
""",

        "PHP": f"""
{PHP_EXAMPLE}
""",

        "React": f"""
{REACT_HOOK_EXAMPLE}
""",

        "Django": f"""
{DJANGO_EXAMPLE}
""",

        "Laravel": f"""
{LARAVEL_EXAMPLE}
""",

        "C#": f"""
{CSHARP_EXAMPLE}
"""
    }

    print("🚀 Cognition Engine Integration Examples")
    print("=" * 60)

    for language, example in examples.items():
        print(f"\n📝 {language} Example:")
        print("-" * 40)
        print(example)


if __name__ == "__main__":
    print_integration_examples()
