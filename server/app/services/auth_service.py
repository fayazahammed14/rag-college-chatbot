from fastapi import Depends, HTTPException, status
from app.utils.security import get_bearer_token
from app.config.db import get_supabase_client
from app.models.profile import ProfileResponse
import logging

logger = logging.getLogger(__name__)


async def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    """
    Validates Supabase JWT, retrieves user information,
    and attaches role from public.profiles table.
    """
    supabase = get_supabase_client()
    try:
        # Verify JWT with Supabase Auth
        auth_response = supabase.auth.get_user(token)
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = auth_response.user
        user_id = str(user.id)
        email = user.email

        # Fetch profile from profiles table to resolve role
        profile_res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if profile_res.data and len(profile_res.data) > 0:
            profile_data = profile_res.data[0]
            name = profile_data.get("name") or email.split("@")[0] if email else "User"
            role = profile_data.get("role", "student")
        else:
            # Fallback: create student profile if trigger hasn't fired yet
            name = (user.user_metadata or {}).get("name") or (email.split("@")[0] if email else "User")
            role = (user.user_metadata or {}).get("role", "student")
            try:
                supabase.table("profiles").insert({
                    "id": user_id,
                    "name": name,
                    "role": role
                }).execute()
            except Exception as e:
                logger.warning(f"Could not auto-create profile row: {e}")

        return {
            "id": user_id,
            "email": email,
            "name": name,
            "role": role
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency ensuring the caller has the 'admin' role.
    """
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to perform this action.",
        )
    return user
