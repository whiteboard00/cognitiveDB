"""
API Authentication and Key Management

Handles API key creation, validation, and rate limiting for the Cognition Engine API.
"""

import secrets
import hashlib
from datetime import datetime
from typing import Dict, Optional, Any
from supabase import Client


class APIKeyManager:
    """Manages API keys for external EdTech platforms"""

    def __init__(self, db: Client):
        self.db = db

    async def create_api_key(self, company_name: str, contact_email: str) -> Dict[str, Any]:
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
            "last_request_at": None,
            "created_at": datetime.now().isoformat()
        }

        result = self.db.table("api_keys").insert(key_data).execute()
        return {
            "api_key": api_key,
            "key_id": result.data[0]["id"],
            "company_name": company_name,
            "created_at": key_data["created_at"]
        }

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and check rate limits"""
        if not api_key:
            return None

        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        result = self.db.table("api_keys").select("*").eq("api_key_hash", hashed_key).eq("is_active", True).execute()

        if not result.data:
            return None

        key_info = result.data[0]

        # Simple rate limiting check (in production, use Redis)
        current_hour = datetime.now().hour
        last_request_hour = key_info.get("last_request_at")

        if last_request_hour:
            try:
                last_hour = datetime.fromisoformat(last_request_hour.replace('Z', '+00:00')).hour
                if current_hour != last_hour:
                    # Reset counter for new hour
                    self.db.table("api_keys").update({
                        "requests_this_hour": 0
                    }).eq("id", key_info["id"]).execute()
                    key_info["requests_this_hour"] = 0
            except:
                pass

        # Check rate limit
        if key_info.get("requests_this_hour", 0) >= key_info.get("rate_limit_per_hour", 1000):
            return None  # Rate limit exceeded

        return key_info

    async def track_api_usage(self, api_key: str, endpoint: str, user_id: Optional[str] = None):
        """Track API usage for billing and analytics"""
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        current_time = datetime.now().isoformat()

        # Increment usage counter
        result = self.db.table("api_keys").select("requests_this_hour").eq("api_key_hash", hashed_key).execute()

        if result.data:
            current_count = result.data[0].get("requests_this_hour", 0) + 1

            self.db.table("api_keys").update({
                "requests_this_hour": current_count,
                "last_request_at": current_time
            }).eq("api_key_hash", hashed_key).execute()

            # Log detailed usage
            self.db.table("api_usage_logs").insert({
                "api_key_hash": hashed_key,
                "endpoint": endpoint,
                "user_id": user_id,
                "timestamp": current_time,
                "request_count": current_count
            }).execute()


# Global instances
api_key_manager = None

def get_api_key_manager(db: Client) -> APIKeyManager:
    """Get or create API key manager instance"""
    global api_key_manager
    if api_key_manager is None:
        api_key_manager = APIKeyManager(db)
    return api_key_manager


async def validate_api_key(api_key: str, db: Client) -> Optional[Dict[str, Any]]:
    """Validate API key for requests"""
    manager = get_api_key_manager(db)
    return await manager.validate_api_key(api_key)


async def track_api_usage(api_key: str, endpoint: str, user_id: Optional[str] = None, db: Client = None):
    """Track API usage for billing"""
    if db:
        manager = get_api_key_manager(db)
        await manager.track_api_usage(api_key, endpoint, user_id)
