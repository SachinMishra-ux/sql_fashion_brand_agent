"""
auth.py
JWT authentication and user profile management for the Fashion Brand AI API.
Provides token creation, verification, and FastAPI dependency get_current_user.
"""
import os
import time
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv

load_dotenv(override=True)

# 256-bit secure secret key for HMAC-SHA256 signing
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "maison_luxe_fashion_brand_super_secure_jwt_secret_key_2025_abcdef123456",
)
ALGORITHM = "HS256"

# 3 demo users matching customer records in the fashion database
DEMO_USERS = [
    {
        "id": "1",
        "name": "Priya Sharma",
        "email": "priya.sharma@email.com",
        "loyalty_tier": "Platinum",
        "avatar": "👑",
    },
    {
        "id": "2",
        "name": "Aisha Khan",
        "email": "aisha.khan@email.com",
        "loyalty_tier": "Gold",
        "avatar": "⭐",
    },
    {
        "id": "3",
        "name": "Riya Verma",
        "email": "riya.verma@email.com",
        "loyalty_tier": "Gold",
        "avatar": "💎",
    },
]


def create_access_token(user: dict, expires_in_seconds: int = 86400 * 30) -> str:
    """
    Creates a signed JWT token containing user identity and metadata.
    """
    now = int(time.time())
    payload = {
        "sub": str(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "loyalty_tier": user.get("loyalty_tier", "Bronze"),
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_demo_users_with_tokens() -> list[dict]:
    """
    Returns the 3 demo users with their signed JWT tokens for frontend consumption.
    """
    return [
        {
            **user,
            "token": create_access_token(user),
        }
        for user in DEMO_USERS
    ]


security = HTTPBearer(auto_error=False)


def verify_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Raises HTTPException 401 if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please authenticate again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    """
    FastAPI security dependency.
    Extracts Bearer token from Authorization header and returns validated user payload.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header with Bearer token. Please log in or select a user profile.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(credentials.credentials)


def resolve_thread_id(
    thread_id: str | None = None,
    user_id: str | int | None = None,
    username: str | None = None,
    current_user: dict | None = None,
) -> str:
    """
    Resolves a target thread ID using any of the available identifiers:
    1. thread_id directly (e.g. 'user_thread_1' or custom string)
    2. user_id (e.g. '1' -> 'user_thread_1')
    3. username / email (e.g. 'Priya Sharma' -> 'user_thread_1')
    4. current_user (from authenticated JWT token)
    """
    if thread_id:
        return thread_id.strip()

    if user_id:
        uid = str(user_id).strip()
        return uid if uid.startswith("user_thread_") else f"user_thread_{uid}"

    if username:
        uname = username.strip().lower()
        # Match against demo users
        for u in DEMO_USERS:
            if uname in (u["name"].lower(), u["email"].lower(), str(u["id"])):
                return f"user_thread_{u['id']}"

        # Match against MySQL database
        try:
            import mysql_db

            rows = mysql_db.run_query(
                f"SELECT id FROM users WHERE LOWER(name) = '{uname}' OR LOWER(email) = '{uname}' LIMIT 1;"
            )
            if rows and "id" in rows[0]:
                return f"user_thread_{rows[0]['id']}"
        except Exception:
            pass

    if current_user and "sub" in current_user:
        return f"user_thread_{current_user['sub']}"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not determine thread ID. Please provide 'thread_id', 'user_id', 'username', or send an Authorization Bearer token.",
    )

