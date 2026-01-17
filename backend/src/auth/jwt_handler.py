from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status, Request
from ..config.settings import settings


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload.

    Args:
        token (str): JWT token to verify

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode the token using the secret key
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user information from payload
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Missing user ID"
            )

        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: Missing expiration"
            )

        # Check if token is expired
        if datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )


async def get_current_user(request: Request) -> str:
    """
    Extract and verify user from JWT token in request headers.

    Args:
        request (Request): FastAPI request object containing Authorization header

    Returns:
        str: User ID extracted from token

    Raises:
        HTTPException: If no token provided or token is invalid
    """
    # Get authorization header
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Check if it's a Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    # Extract token
    token = authorization.split(" ")[1]

    # Verify token and get payload
    payload = verify_token(token)

    # Return user ID
    return payload.get("sub")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token with the provided data.

    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Token expiration time delta

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire.timestamp()})

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token without full verification (for logging/debugging).

    Args:
        token (str): JWT token to extract user ID from

    Returns:
        str: User ID if found, None otherwise
    """
    try:
        # Decode without verification to get user ID
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None