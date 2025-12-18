"""
Authentication Router - STEP 13
Drop-in authentication endpoints with JWT + Refresh Token support
"""
from fastapi import APIRouter, Response, HTTPException, status
from app.auth.jwt import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(response: Response):
    """
    Login endpoint that demonstrates JWT token generation and secure cookie setting.
    
    In a real implementation, this would:
    1. Validate user credentials (email/password)
    2. Query database to verify user exists
    3. Use the actual user ID from the database
    
    This example shows the token generation and cookie setup pattern.
    """
    # TODO: Replace with actual user validation
    # Example:
    # user = await db.execute(select(User).where(User.email == email))
    # if not user or not verify_password(password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = "123"  # TODO: Replace with actual user ID from database
    
    # Create access and refresh tokens
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    
    # Set access token cookie
    # httponly=True prevents JavaScript access (XSS protection)
    # secure=True requires HTTPS (production security)
    # samesite="None" allows cross-origin requests (needed for frontend/backend on different domains)
    # max_age=900 is 15 minutes in seconds
    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=900,  # 15 minutes
    )
    
    # Set refresh token cookie
    # max_age=604800 is 7 days in seconds
    response.set_cookie(
        "refresh_token",
        refresh,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=604800,  # 7 days
    )
    
    return {"status": "logged_in", "user_id": user_id}


@router.post("/logout")
def logout(response: Response):
    """
    Logout endpoint that clears authentication cookies.
    
    CRITICAL: Uses delete_cookie() with path="/" to ensure proper cookie removal
    and prevent "ghost login" issues.
    """
    response.delete_cookie(
        "access_token",
        path="/",
        samesite="None",
        secure=True
    )
    response.delete_cookie(
        "refresh_token",
        path="/",
        samesite="None",
        secure=True
    )
    
    return {"status": "logged_out"}


@router.post("/refresh")
def refresh(response: Response):
    """
    Refresh endpoint to get a new access token using the refresh token.
    
    In a real implementation, this would:
    1. Extract refresh token from cookie
    2. Validate refresh token
    3. Verify refresh token in database
    4. Generate new access token
    """
    # TODO: Implement refresh token validation
    # Example:
    # refresh_token = request.cookies.get("refresh_token")
    # payload = decode_token(refresh_token)
    # user_id = payload.get("sub")
    
    user_id = "123"  # TODO: Extract from validated refresh token
    
    # Create new access token
    access = create_access_token(user_id)
    
    # Set new access token cookie
    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=900,  # 15 minutes
    )
    
    return {"status": "token_refreshed"}
