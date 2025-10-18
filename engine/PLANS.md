# 🚀 Cognition Engine API - Implementation Plan

## 🎯 **Goal: Transform SDK into Monetizable API Service**

**Current State:** Sophisticated learning analytics code
**Target State:** Live API service at `api.cognition-engine.com` that EdTech companies pay for

---

## 📊 **Current Assessment**

### **✅ Strengths (Excellent Foundation)**

- **Advanced Algorithms**: BKT, velocity tracking, predictive analytics, cognitive efficiency
- **Production-Ready Code**: Well-structured, error handling, comprehensive logging
- **Vector Database Ready**: Framework for semantic search and similarity matching
- **Comprehensive Documentation**: README, migration guides, examples

### **🔴 Gaps for Monetization**

- **No API Endpoints**: Just Python classes, not HTTP services
- **No Authentication**: No API key management for customers
- **No Deployment**: No Docker, no cloud deployment
- **No Billing**: No usage tracking or payment processing
- **No Documentation**: No API reference for external developers

---

## 🏗️ **Phase 1: Minimum Viable API (2-3 weeks)**

### **Week 1: API Key Authentication & Core Endpoints**

#### **1.1 API Key Management System**

```python
# engine/api_auth.py (NEW FILE)
import secrets
import hashlib
from datetime import datetime
from supabase import Client

class APIKeyManager:
    def __init__(self, db: Client):
        self.db = db

    async def create_api_key(self, company_name: str, contact_email: str) -> Dict:
        """Create new API key for EdTech customer"""
        api_key = secrets.token_urlsafe(32)
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()

        key_data = {
            "company_name": company_name,
            "contact_email": contact_email,
            "api_key_hash": hashed_key,
            "is_active": True,
            "rate_limit_per_hour": 1000,
            "requests_this_hour": 0,
            "created_at": datetime.now().isoformat()
        }

        result = self.db.table("api_keys").insert(key_data).execute()
        return {"api_key": api_key, "key_id": result.data[0]["id"]}

    async def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and check rate limits"""
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        result = self.db.table("api_keys").select("*").eq("api_key_hash", hashed_key).eq("is_active", True).execute()

        if not result.data:
            return None

        key_info = result.data[0]

        # Check rate limit
        if key_info.get("requests_this_hour", 0) >= key_info.get("rate_limit_per_hour", 1000):
            return None

        return key_info
```

#### **1.2 Core API Endpoints**

```python
# engine/api_endpoints.py (NEW FILE)
from fastapi import APIRouter, Depends, HTTPException, Header
from cognition_engine import CognitionEngine

router = APIRouter(prefix="/api/v1", tags=["cognition-api"])

@router.post("/track-answer")
async def track_learning_event(
    user_id: str,
    skill_id: str,
    is_correct: bool,
    time_spent_seconds: Optional[int] = None,
    confidence_score: Optional[int] = None,
    question_difficulty: Optional[float] = None,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Main endpoint for tracking learning events"""

    # Validate API key
    key_info = await validate_api_key(api_key)
    if not key_info:
        raise HTTPException(401, "Invalid API key")

    # Track the answer
    result = await cognition_engine.track_answer(
        user_id=user_id,
        skill_id=skill_id,
        is_correct=is_correct,
        time_spent_seconds=time_spent_seconds,
        confidence_score=confidence_score,
        question_difficulty=question_difficulty
    )

    # Track usage for billing
    await track_api_usage(api_key, "/track-answer", user_id)

    return result

@router.get("/predictions/{user_id}")
async def get_predictions(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Get predictive analytics for a user"""
    key_info = await validate_api_key(api_key)
    if not key_info:
        raise HTTPException(401, "Invalid API key")

    result = await cognition_engine.get_predictions(user_id)
    await track_api_usage(api_key, "/predictions", user_id)

    return result

@router.get("/velocity/{user_id}")
async def get_learning_velocity(
    user_id: str,
    api_key: str = Header(..., alias="X-API-Key")
):
    """Get learning velocity metrics"""
    key_info = await validate_api_key(api_key)
    if not key_info:
        raise HTTPException(401, "Invalid API key")

    result = await cognition_engine.get_learning_velocity(user_id)
    await track_api_usage(api_key, "/velocity", user_id)

    return result

@router.post("/batch-track")
async def batch_track_answers(
    events: List[Dict],
    api_key: str = Header(..., alias="X-API-Key")
):
    """Batch process multiple learning events"""
    key_info = await validate_api_key(api_key)
    if not key_info:
        raise HTTPException(401, "Invalid API key")

    result = await cognition_engine.batch_track_answers(events)
    await track_api_usage(api_key, "/batch-track", user_id=None)

    return result
```

#### **1.3 FastAPI Application**

```python
# engine/main.py (NEW FILE)
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import os

# Import our API components
from .api_auth import APIKeyManager, validate_api_key
from .api_endpoints import router as cognition_router
from .cognition_engine import CognitionEngine

# Initialize FastAPI app
app = FastAPI(
    title="Cognition Engine API",
    description="Advanced learning analytics and prediction API for EdTech platforms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key validation middleware
@app.middleware("http")
async def validate_api_key_middleware(request: Request, call_next):
    """Validate API keys for all /api/v1 requests"""
    if request.url.path.startswith("/api/v1"):
        api_key = request.headers.get("X-API-Key")
        if not api_key or not await validate_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API key"}
            )
    return await call_next(request)

# Include API routers
app.include_router(cognition_router)

@app.get("/")
async def root():
    return {"message": "Cognition Engine API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cognition-engine"}

# Admin endpoints (protected by master key)
@app.post("/admin/create-api-key")
async def create_customer_api_key(
    company_name: str,
    contact_email: str,
    master_key: str = Header(...)
):
    """Create new API key for customer (admin only)"""
    if master_key != os.getenv("MASTER_API_KEY"):
        raise HTTPException(403, "Invalid master key")

    api_key_manager = APIKeyManager(get_db())
    return await api_key_manager.create_api_key(company_name, contact_email)
```

### **Week 2: Vector Database & Production Setup**

#### **2.1 Real Vector Database Integration**

```python
# Update cognition_engine.py - replace placeholder embeddings
import openai
import chromadb

class RealEmbeddingService:
    def __init__(self, openai_api_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")

    async def generate_text_embedding(self, text: str) -> List[float]:
        """Generate real OpenAI text embeddings"""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def generate_code_embedding(self, code: str) -> List[float]:
        """Generate code embeddings for similarity detection"""
        response = self.openai_client.embeddings.create(
            input=f"Code: {code}",
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

# Update CognitionEngine initialization
cognition_engine = CognitionEngine(
    supabase_url=settings.supabase_url,
    supabase_key=settings.supabase_anon_key,
    embedding_service=RealEmbeddingService(settings.openai_api_key)
)
```

#### **2.2 Production Configuration**

```python
# engine/config.py (NEW FILE)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    supabase_url: str
    supabase_anon_key: str

    # OpenAI
    openai_api_key: str

    # Vector Database
    vector_db_path: str = "./chroma_db"

    # API Keys
    master_api_key: str

    # Rate Limiting
    default_rate_limit: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### **2.3 Docker Configuration**

```dockerfile
# engine/Dockerfile (NEW FILE)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create vector database directory
RUN mkdir -p /app/chroma_db

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **2.4 Database Migration for API Keys**

```sql
-- engine/migrations/001_add_api_keys.sql (NEW FILE)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(64) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_hour INTEGER DEFAULT 1000,
    requests_this_hour INTEGER DEFAULT 0,
    last_request_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_hash VARCHAR(64) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW(),
    request_count INTEGER
);

-- Indexes for performance
CREATE INDEX idx_api_keys_hash ON api_keys(api_key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_usage_logs_timestamp ON api_usage_logs(timestamp);
CREATE INDEX idx_usage_logs_key ON api_usage_logs(api_key_hash);
```

### **Week 3: Documentation & Testing**

#### **3.1 API Documentation**

```python
# Automatic OpenAPI/Swagger documentation
app = FastAPI(
    title="Cognition Engine API",
    description="""
    Advanced learning analytics and prediction API for EdTech platforms.

    ## Authentication
    All API requests require an API key in the X-API-Key header.

    ## Rate Limits
    - Starter: 1,000 requests/hour
    - Professional: 10,000 requests/hour
    - Enterprise: Unlimited

    ## Support
    Contact: support@cognition-engine.com
    """,
    version="1.0.0"
)
```

#### **3.2 Integration Examples**

```python
# engine/integration_examples.py (NEW FILE)
class CognitionEngineAPI:
    """Python client for Cognition Engine API"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def track_answer(self, user_id: str, skill_id: str, **kwargs):
        """Track a learning event"""
        response = requests.post(
            f"{self.base_url}/api/v1/track-answer",
            headers={"X-API-Key": self.api_key},
            json={"user_id": user_id, "skill_id": skill_id, **kwargs}
        )
        return response.json()

    async def get_predictions(self, user_id: str):
        """Get predictive analytics"""
        response = requests.get(
            f"{self.base_url}/api/v1/predictions/{user_id}",
            headers={"X-API-Key": self.api_key}
        )
        return response.json()

# Usage example for EdTech customers
async def example_integration():
    client = CognitionEngineAPI(
        base_url="https://api.cognition-engine.com",
        api_key="customer-api-key"
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
```

#### **3.3 Testing Suite**

```python
# engine/test_api.py (NEW FILE)
import pytest
from fastapi.testclient import TestClient

def test_track_answer_endpoint():
    """Test the main tracking endpoint"""
    response = client.post(
        "/api/v1/track-answer",
        headers={"X-API-Key": "test-key"},
        json={
            "user_id": "test_user",
            "skill_id": "test_skill",
            "is_correct": True
        }
    )
    assert response.status_code == 200
    assert "mastery_after" in response.json()

def test_invalid_api_key():
    """Test API key validation"""
    response = client.post(
        "/api/v1/track-answer",
        headers={"X-API-Key": "invalid-key"},
        json={"user_id": "test", "skill_id": "test", "is_correct": True}
    )
    assert response.status_code == 401
```

---

## 🚀 **Phase 2: Production Service (2-3 weeks)**

### **4. Deployment & Infrastructure**

#### **4.1 Cloud Deployment (Railway/Render)**

```yaml
# railway.toml (NEW FILE)
[build]
builder = "docker"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"

[services]
cognition-api = { src: ".", type: "web" }
```

#### **4.2 Environment Configuration**

```bash
# .env.example (NEW FILE)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
MASTER_API_KEY=your-master-key-for-admin-operations
VECTOR_DB_PATH=./chroma_db
LOG_LEVEL=INFO
```

#### **4.3 Monitoring & Logging**

```python
# engine/monitoring.py (NEW FILE)
import logging
from datetime import datetime

class APIMonitor:
    def __init__(self):
        self.logger = logging.getLogger("cognition-api")

    async def log_request(self, api_key: str, endpoint: str, user_id: str = None):
        """Log API request for monitoring"""
        self.logger.info(f"API Request: {endpoint} | Key: {api_key[:8]}... | User: {user_id}")

    async def log_error(self, error: Exception, endpoint: str, api_key: str = None):
        """Log API errors"""
        self.logger.error(f"API Error in {endpoint}: {str(error)} | Key: {api_key}")

    async def get_usage_stats(self, timeframe_days: int = 30):
        """Get usage statistics for billing"""
        # Query database for usage data
        return {
            "total_requests": 100000,
            "unique_users": 1500,
            "top_endpoints": ["/track-answer", "/predictions"],
            "error_rate": 0.02
        }
```

### **5. Customer Management**

#### **5.1 Customer Dashboard**

```python
# Simple admin dashboard for managing customers
@router.get("/admin/customers")
async def get_customers(
    master_key: str = Header(...)
):
    """Get all customers and their usage"""
    if master_key != settings.master_api_key:
        raise HTTPException(403, "Invalid master key")

    # Query database for customer data
    customers = db.table("api_keys").select("*").execute()
    return {"customers": customers.data}

@router.get("/admin/usage/{customer_id}")
async def get_customer_usage(
    customer_id: str,
    master_key: str = Header(...),
    timeframe_days: int = 30
):
    """Get usage statistics for specific customer"""
    if master_key != settings.master_api_key:
        raise HTTPException(403, "Invalid master key")

    # Query usage logs for customer
    usage = db.table("api_usage_logs").select("*").eq("api_key_hash", customer_id).execute()
    return {"usage": usage.data}
```

#### **5.2 Billing Integration**

```python
# engine/billing.py (NEW FILE)
import stripe

class BillingManager:
    def __init__(self, stripe_secret_key: str):
        self.stripe = stripe.StripeClient(stripe_secret_key)

    async def create_customer(self, email: str, company_name: str):
        """Create Stripe customer"""
        customer = self.stripe.customers.create(
            email=email,
            name=company_name
        )
        return customer.id

    async def create_subscription(self, customer_id: str, price_id: str):
        """Create subscription for customer"""
        subscription = self.stripe.subscriptions.create(
            customer=customer_id,
            items=[{"price": price_id}]
        )
        return subscription.id

    async def get_usage_for_billing(self, customer_id: str, start_date: str, end_date: str):
        """Get usage data for billing period"""
        usage = db.table("api_usage_logs").select("*").eq("api_key_hash", customer_id).execute()
        return len(usage.data)
```

---

## 💰 **Monetization Strategy**

### **Pricing Tiers**

```python
@router.get("/pricing")
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
```

### **Customer Onboarding Flow**

1. **Sign Up**: Customer provides company info and email
2. **API Key Creation**: Admin creates API key for customer
3. **Integration**: Customer integrates with 5 lines of code
4. **Billing**: Automatic billing based on usage
5. **Support**: Access to documentation and support

---

## 📋 **Implementation Checklist**

### **Week 1: Core API (✅ Foundation Exists)**

- [x] Cognition Engine algorithms (already built)
- [ ] API key authentication system
- [ ] Core HTTP endpoints (/track-answer, /predictions, /velocity)
- [ ] Request validation and error handling
- [ ] Usage tracking for billing

### **Week 2: Production Infrastructure**

- [ ] Real OpenAI embeddings integration
- [ ] ChromaDB setup with persistent storage
- [ ] Docker containerization
- [ ] Environment configuration
- [ ] Rate limiting implementation

### **Week 3: Documentation & Testing**

- [ ] FastAPI automatic documentation
- [ ] Integration examples for customers
- [ ] API testing suite
- [ ] Health checks and monitoring
- [ ] Error tracking setup

### **Week 4: Deployment & Launch**

- [ ] Cloud deployment (Railway/Render)
- [ ] Custom domain setup (api.cognition-engine.com)
- [ ] Customer onboarding documentation
- [ ] Billing system integration
- [ ] Admin dashboard for monitoring

---

## 🎯 **Success Metrics**

### **Technical Success**

- **Live API**: `https://api.cognition-engine.com` responding
- **Authentication**: API key validation working
- **Rate Limiting**: Proper request throttling
- **Error Handling**: Graceful error responses
- **Documentation**: Auto-generated API docs

### **Business Success**

- **Customer Integration**: EdTech companies can integrate with API key
- **Usage Tracking**: Accurate billing data collection
- **Scalability**: Handles 1000+ requests/hour
- **Reliability**: 99.9% uptime

### **Customer Experience**

```python
# What customers can do:
import requests

# Track learning
response = requests.post(
    "https://api.cognition-engine.com/api/v1/track-answer",
    headers={"X-API-Key": "their-api-key"},
    json={
        "user_id": "student_123",
        "skill_id": "algebra",
        "is_correct": True,
        "time_spent_seconds": 75,
        "confidence_score": 4
    }
)

# Get insights
predictions = requests.get(
    "https://api.cognition-engine.com/api/v1/predictions/student_123",
    headers={"X-API-Key": "their-api-key"}
).json()

print(f"Predicted score: {predictions['predicted_total_in_30_days']}")
```

---

## 🚦 **Next Steps**

1. **Start Building**: Begin with API key authentication system
2. **Test Locally**: Get endpoints working with Postman/curl
3. **Deploy**: Push to Railway/Render for live testing
4. **Customer Acquisition**: Find EdTech companies to beta test
5. **Iterate**: Improve based on customer feedback

---

## 💡 **Key Files to Create**

1. **`api_auth.py`** - API key management and validation
2. **`api_endpoints.py`** - HTTP endpoints for all SDK methods
3. **`main.py`** - FastAPI application setup
4. **`config.py`** - Settings and configuration
5. **`Dockerfile`** - Container configuration
6. **`requirements.txt`** - Updated with FastAPI dependencies
7. **`integration_examples.py`** - Customer integration code
8. **`test_api.py`** - API testing suite

---

**Ready to build the monetizable API service?** 🚀

This plan transforms sophisticated algorithms into a **business-ready API** that EdTech companies will pay for.</response>
</write_to_file>
