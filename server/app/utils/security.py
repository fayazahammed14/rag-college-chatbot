from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security_bearer = HTTPBearer(auto_error=False)


async def get_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)
) -> str:
    """Extracts the Bearer token from the Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
