from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user
from app.models.profile import ProfileResponse

router = APIRouter(tags=["Health & Profile"])


@router.get("/health")
async def health_check():
    """System heartbeat endpoint."""
    return {
        "status": "healthy",
        "service": "CampusMind AI API",
        "version": "1.0.0"
    }


@router.get("/profile/me", response_model=ProfileResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Verify Supabase JWT token and return caller's profile with resolved role."""
    return ProfileResponse(
        id=current_user["id"],
        email=current_user.get("email"),
        name=current_user.get("name"),
        role=current_user.get("role", "student")
    )
